"""Traitement PySpark — lit les données agrégées du Data Lake, les nettoie et
les charge dans PostgreSQL. Tourne en boucle (relit l'ensemble du fichier à
chaque cycle ; idempotent grâce à l'upsert ON CONFLICT DO NOTHING).

Nettoyage appliqué :
- contrôle des types (surfaces, prix, dates) ;
- rejet des étiquettes DPE/GES hors A-G ;
- rejet des lignes sans identifiant ou commune ;
- déduplication sur numero_dpe ;
- rejet des communes hors référentiel (FK vers `commune`, cf. TP1).

C'est cette étape qui expose l'indicateur Prometheus « clean_records_total »
(volume de données propres effectivement chargées dans PostgreSQL) — la
comparaison avec « raw_records_total
(exposé par l'agrégateur) donne l'indicateur Raw vs Clean demandé.
"""
import os
import time

import psycopg2
import psycopg2.extras
from prometheus_client import Gauge, start_http_server
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import BooleanType, DoubleType

DATALAKE = os.environ.get("DATALAKE_ROOT", "/datalake")
AGG_INPUT = f"{DATALAKE}/aggregated/dpe_enrichi.ndjson"
INTERVAL = int(os.environ.get("SPARK_INTERVAL_SECONDS", "60"))
METRICS_PORT = int(os.environ.get("METRICS_PORT", "8000"))

PG_DSN = dict(
    host=os.environ.get("PG_HOST", "db"),
    port=os.environ.get("PG_PORT", "5432"),
    dbname=os.environ.get("PG_DB", "audit_immo_energie_44"),
    user=os.environ.get("PG_USER", "postgres"),
    password=os.environ.get("PG_PASSWORD", "postgres"),
)

CLEAN_RECORDS = Gauge("clean_records_total", "Lignes propres chargées dans PostgreSQL (diagnostic_dpe_flux)")
VALID_ETIQUETTES = ["A", "B", "C", "D", "E", "F", "G"]


def get_valid_communes(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT code_insee FROM commune")
        return {row[0] for row in cur.fetchall()}


def upsert(conn, rows):
    if not rows:
        return 0
    sql = """
        INSERT INTO diagnostic_dpe_flux
            (numero_dpe, code_insee, date_reception_dpe, etiquette_dpe, etiquette_ges,
             surface_habitable_logement, prix_m2_commune_reference, source_flux)
        VALUES %s
        ON CONFLICT (numero_dpe) DO NOTHING
    """
    values = [
        (
            r["numero_dpe"], r["code_insee"], r["date_reception_dpe"],
            r["etiquette_dpe"], r["etiquette_ges"], r["surface_habitable_logement"],
            r["prix_m2_commune_reference"], r["source_flux"],
        )
        for r in rows
    ]
    with conn.cursor() as cur:
        psycopg2.extras.execute_values(cur, sql, values, page_size=2000)
    conn.commit()
    return len(values)


def run_cycle(spark, conn):
    if not os.path.exists(AGG_INPUT) or os.path.getsize(AGG_INPUT) == 0:
        print("[spark] rien à traiter pour l'instant")
        return

    df = spark.read.json(AGG_INPUT)

    df = (
        df.withColumn("surface_habitable_logement", F.col("surface_habitable_logement").cast(DoubleType()))
        .withColumn("prix_m2_commune_reference", F.col("prix_m2_commune_reference").cast(DoubleType()))
        .withColumn("date_reception_dpe", F.to_date("date_reception_dpe"))
        .filter(F.col("numero_dpe").isNotNull())
        .filter(F.col("code_insee").isNotNull())
        .filter(F.col("etiquette_dpe").isin(VALID_ETIQUETTES))
        .filter(F.col("etiquette_ges").isin(VALID_ETIQUETTES))
        .dropDuplicates(["numero_dpe"])
    )

    valid_communes = get_valid_communes(conn)
    valid_communes_bc = spark.sparkContext.broadcast(valid_communes)
    is_valid_commune = F.udf(lambda c: c in valid_communes_bc.value, BooleanType())
    df = df.filter(is_valid_commune(F.col("code_insee")))

    rows = [r.asDict() for r in df.collect()]
    n_loaded = upsert(conn, rows)

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM diagnostic_dpe_flux")
        total = cur.fetchone()[0]
    CLEAN_RECORDS.set(total)

    print(f"[spark] cycle : {len(rows)} lignes propres traitées, {total} lignes en base au total")


def main():
    start_http_server(METRICS_PORT)
    spark = SparkSession.builder.appName("tp2-dpe-clean-load").master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    while True:
        try:
            conn = psycopg2.connect(**PG_DSN)
            try:
                run_cycle(spark, conn)
            finally:
                conn.close()
        except Exception as e:
            print(f"[spark] erreur pendant le cycle : {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
