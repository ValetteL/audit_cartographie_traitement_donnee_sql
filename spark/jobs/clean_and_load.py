"""Spark Structured Streaming — consomme directement le topic Kafka `dpe-flux-44`
(Source 1), dépose le brut et l'enrichi dans le Data Lake, nettoie et charge
dans PostgreSQL. Fusionne ce qui était avant deux composants séparés
(un consommateur Kafka fait main + un relecteur de fichiers en boucle) en une
seule requête de streaming, avec checkpointing Kafka natif : reprise correcte
après un crash (offsets gérés par Spark), plutôt qu'un consumer group manuel à
l'auto-commit périodique et des écritures fichier sans garantie de reprise.

Par micro-batch (toutes les SPARK_INTERVAL_SECONDS) :
- dépôt du flux brut dans raw/api/dpe_raw.ndjson (couche brute, non filtrée) ;
- enrichissement avec le prix moyen au m² de la commune (raw/source2/, chargé
  une fois au démarrage, cf. source2-loader) -> aggregated/dpe_enrichi.ndjson ;
- nettoyage : types, étiquettes DPE/GES dans A-G, déduplication sur
  numero_dpe, rejet des communes hors référentiel (FK vers `commune`) ;
- upsert dans diagnostic_dpe_flux (ON CONFLICT DO NOTHING, idempotent).

Expose raw_records_total et clean_records_total (indicateur Raw vs Clean).
"""
import json
import os
import time

import psycopg2
import psycopg2.extras
from prometheus_client import Gauge, start_http_server
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructField, StructType

DATALAKE = os.environ.get("DATALAKE_ROOT", "/datalake")
RAW_OUT = f"{DATALAKE}/raw/api/dpe_raw.ndjson"
AGG_OUT = f"{DATALAKE}/aggregated/dpe_enrichi.ndjson"
PRIX_COMMUNE_CSV = f"{DATALAKE}/raw/source2/prix_moyen_commune.csv"
CHECKPOINT_DIR = f"{DATALAKE}/checkpoints/spark"

KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:19092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "dpe-flux-44")
TRIGGER_INTERVAL = os.environ.get("SPARK_INTERVAL_SECONDS", "60") + " seconds"
METRICS_PORT = int(os.environ.get("METRICS_PORT", "8000"))

PG_DSN = dict(
    host=os.environ.get("PG_HOST", "db"),
    port=os.environ.get("PG_PORT", "5432"),
    dbname=os.environ.get("PG_DB", "audit_immo_energie_44"),
    user=os.environ.get("PG_USER", "postgres"),
    password=os.environ.get("PG_PASSWORD", "postgres"),
)

RAW_RECORDS = Gauge("raw_records_total", "Enregistrements bruts déposés dans le Data Lake")
CLEAN_RECORDS = Gauge("clean_records_total", "Lignes propres chargées dans PostgreSQL (diagnostic_dpe_flux)")
VALID_ETIQUETTES = {"A", "B", "C", "D", "E", "F", "G"}

EVENT_SCHEMA = StructType([
    StructField("numero_dpe", StringType()),
    StructField("code_insee", StringType()),
    StructField("date_reception_dpe", StringType()),
    StructField("etiquette_dpe", StringType()),
    StructField("etiquette_ges", StringType()),
    StructField("surface_habitable_logement", StringType()),
    StructField("source_flux", StringType()),
])


def count_existing_lines(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as f:
        return sum(1 for _ in f)


def load_prix_commune(spark):
    if not os.path.exists(PRIX_COMMUNE_CSV):
        print(f"[spark] {PRIX_COMMUNE_CSV} introuvable, poursuite sans enrichissement prix")
        return {}
    rows = spark.read.option("header", True).csv(PRIX_COMMUNE_CSV).collect()
    return {r["code_insee"]: float(r["prix_m2_moyen"]) for r in rows}


def connect_pg_with_retry():
    for attempt in range(30):
        try:
            return psycopg2.connect(**PG_DSN)
        except Exception as e:
            print(f"[spark] PostgreSQL indisponible ({e}), retry {attempt + 1}/30...")
            time.sleep(2)
    raise RuntimeError("Impossible de se connecter à PostgreSQL")


def get_valid_communes(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT code_insee FROM commune")
        return {row[0] for row in cur.fetchall()}


def clean_row(event, prix, valid_communes):
    numero_dpe = event.get("numero_dpe")
    code_insee = event.get("code_insee")
    etiquette_dpe = event.get("etiquette_dpe")
    etiquette_ges = event.get("etiquette_ges")
    if not numero_dpe or not code_insee:
        return None
    if etiquette_dpe not in VALID_ETIQUETTES or etiquette_ges not in VALID_ETIQUETTES:
        return None
    if code_insee not in valid_communes:
        return None
    try:
        surface = float(event["surface_habitable_logement"])
    except (TypeError, ValueError, KeyError):
        surface = None
    return (
        numero_dpe, code_insee, event.get("date_reception_dpe"),
        etiquette_dpe, etiquette_ges, surface,
        prix.get(code_insee), event.get("source_flux"),
    )


def upsert(conn, rows):
    if not rows:
        return
    sql = """
        INSERT INTO diagnostic_dpe_flux
            (numero_dpe, code_insee, date_reception_dpe, etiquette_dpe, etiquette_ges,
             surface_habitable_logement, prix_m2_commune_reference, source_flux)
        VALUES %s
        ON CONFLICT (numero_dpe) DO NOTHING
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_values(cur, sql, rows, page_size=2000)
    conn.commit()


def main():
    start_http_server(METRICS_PORT)
    os.makedirs(os.path.dirname(RAW_OUT), exist_ok=True)
    os.makedirs(os.path.dirname(AGG_OUT), exist_ok=True)

    spark = SparkSession.builder.appName("tp2-dpe-stream").master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    prix_commune = load_prix_commune(spark)

    conn = connect_pg_with_retry()
    valid_communes = get_valid_communes(conn)
    conn.close()

    raw_count = count_existing_lines(RAW_OUT)
    RAW_RECORDS.set(raw_count)
    state = {"raw_count": raw_count}

    def process_batch(batch_df, batch_id):
        events = [r.asDict() for r in batch_df.collect()]
        if not events:
            return

        with open(RAW_OUT, "a", encoding="utf-8") as raw_f, open(AGG_OUT, "a", encoding="utf-8") as agg_f:
            for e in events:
                raw_f.write(json.dumps(e) + "\n")
                enrichi = dict(e)
                enrichi["prix_m2_commune_reference"] = prix_commune.get(e.get("code_insee"))
                agg_f.write(json.dumps(enrichi) + "\n")

        state["raw_count"] += len(events)
        RAW_RECORDS.set(state["raw_count"])

        cleaned = {}
        for e in events:
            row = clean_row(e, prix_commune, valid_communes)
            if row is not None:
                cleaned[row[0]] = row  # dédup sur numero_dpe, dernière occurrence du batch

        pg_conn = connect_pg_with_retry()
        try:
            upsert(pg_conn, list(cleaned.values()))
            with pg_conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM diagnostic_dpe_flux")
                total = cur.fetchone()[0]
            CLEAN_RECORDS.set(total)
        finally:
            pg_conn.close()

        print(f"[spark] batch {batch_id} : {len(events)} événements reçus, "
              f"{len(cleaned)} lignes propres, {total} lignes en base au total")

    for attempt in range(30):
        try:
            kafka_df = (
                spark.readStream.format("kafka")
                .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
                .option("subscribe", KAFKA_TOPIC)
                .option("startingOffsets", "earliest")
                .load()
            )
            break
        except Exception as e:
            print(f"[spark] Kafka indisponible ({e}), retry {attempt + 1}/30...")
            time.sleep(3)
    else:
        raise RuntimeError("Impossible de se connecter à Kafka")

    events_df = kafka_df.select(
        F.from_json(F.col("value").cast("string"), EVENT_SCHEMA).alias("e")
    ).select("e.*")

    query = (
        events_df.writeStream
        .foreachBatch(process_batch)
        .option("checkpointLocation", CHECKPOINT_DIR)
        .trigger(processingTime=TRIGGER_INTERVAL)
        .start()
    )
    query.awaitTermination()


if __name__ == "__main__":
    main()
