"""Agrégation — consomme le flux Kafka (Source 1, DPE), le dépose tel quel dans
le Data Lake (raw/api/), l'enrichit avec le prix moyen au m² de la commune
(Source 2, DVF, déjà chargé par source2/loader.py), et dépose le résultat
dans aggregated/.

C'est cette étape qui expose l'indicateur Prometheus « raw_records_total »
(volume de données brutes effectivement déposées dans le Data Lake).
"""
import csv
import json
import os
import time

from kafka import KafkaConsumer
from prometheus_client import Gauge, start_http_server

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:19092")
TOPIC = os.environ.get("KAFKA_TOPIC", "dpe-flux-44")
DATALAKE = os.environ.get("DATALAKE_ROOT", "/datalake")
PRIX_COMMUNE_CSV = os.environ.get(
    "PRIX_COMMUNE_CSV", f"{DATALAKE}/raw/source2/prix_moyen_commune.csv"
)
RAW_OUT = f"{DATALAKE}/raw/api/dpe_raw.ndjson"
AGG_OUT = f"{DATALAKE}/aggregated/dpe_enrichi.ndjson"
METRICS_PORT = int(os.environ.get("METRICS_PORT", "8000"))

RAW_RECORDS = Gauge("raw_records_total", "Enregistrements bruts déposés dans le Data Lake")


def count_existing_lines(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as f:
        return sum(1 for _ in f)


def load_prix_commune():
    prix = {}
    for attempt in range(30):
        if os.path.exists(PRIX_COMMUNE_CSV):
            with open(PRIX_COMMUNE_CSV, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    prix[row["code_insee"]] = float(row["prix_m2_moyen"])
            print(f"[aggregator] {len(prix)} communes chargées depuis {PRIX_COMMUNE_CSV}")
            return prix
        print(f"[aggregator] en attente de {PRIX_COMMUNE_CSV} (source2)...")
        time.sleep(2)
    print("[aggregator] source2 introuvable après 60s, poursuite sans enrichissement prix")
    return prix


def make_consumer():
    for attempt in range(20):
        try:
            return KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                group_id="aggregator",
                auto_offset_reset="earliest",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            )
        except Exception as e:
            print(f"[aggregator] Kafka indisponible ({e}), retry {attempt + 1}/20...")
            time.sleep(3)
    raise RuntimeError("Impossible de se connecter à Kafka")


def main():
    start_http_server(METRICS_PORT)
    os.makedirs(os.path.dirname(RAW_OUT), exist_ok=True)
    os.makedirs(os.path.dirname(AGG_OUT), exist_ok=True)

    prix_commune = load_prix_commune()
    consumer = make_consumer()
    print("[aggregator] à l'écoute de Kafka...")

    # Repart du volume réellement déjà déposé (fichier persistant sur le volume
    # Data Lake) et non de zéro, pour que raw_records_total reste comparable à
    # clean_records_total (recalculé depuis PostgreSQL) même après un redémarrage.
    count = count_existing_lines(RAW_OUT)
    RAW_RECORDS.set(count)
    with open(RAW_OUT, "a", encoding="utf-8") as raw_f, open(AGG_OUT, "a", encoding="utf-8") as agg_f:
        for message in consumer:
            event = message.value
            raw_f.write(json.dumps(event) + "\n")
            raw_f.flush()

            enrichi = dict(event)
            enrichi["prix_m2_commune_reference"] = prix_commune.get(event.get("code_insee"))
            agg_f.write(json.dumps(enrichi) + "\n")
            agg_f.flush()

            count += 1
            RAW_RECORDS.set(count)
            if count % 2000 == 0:
                print(f"[aggregator] {count} événements traités")


if __name__ == "__main__":
    main()
