"""Producer Kafka — Source 1 (API DPE, ADEME).

Deux phases :
1. Backfill : rejoue les DPE déjà collectés en TP1 (data/staging/diagnostic_dpe.csv,
   352k lignes) à débit contrôlé, pour garantir un flux visible dès le démarrage
   (le jeu de données réel de l'ADEME ne produit que quelques nouveaux DPE par
   semaine pour le seul département 44 — insuffisant pour une démo courte).
2. Live : interroge ensuite l'API ADEME en continu pour les diagnostics réellement
   nouveaux (date_reception_dpe postérieure au dernier vu), et les publie au fil de l'eau.

Chaque événement Kafka a le même schéma, avec un champ `source_flux` qui distingue
les deux origines.
"""
import csv
import json
import os
import time
import urllib.parse
import urllib.request

from kafka import KafkaProducer
from prometheus_client import Counter, start_http_server

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:19092")
TOPIC = os.environ.get("KAFKA_TOPIC", "dpe-flux-44")
BACKFILL_CSV = os.environ.get("BACKFILL_CSV", "/data/staging/diagnostic_dpe.csv")
BACKFILL_RATE = float(os.environ.get("BACKFILL_RATE_PER_SEC", "200"))
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL_SECONDS", "300"))
DEPARTEMENT = os.environ.get("DEPARTEMENT", "44")
WATERMARK_FILE = os.environ.get("WATERMARK_FILE", "/state/watermark.txt")
BACKFILL_DONE_FILE = os.environ.get("BACKFILL_DONE_FILE", "/state/backfill_done")
METRICS_PORT = int(os.environ.get("METRICS_PORT", "8000"))

EVENTS_PUBLISHED = Counter(
    "producer_events_published_total", "Événements DPE publiés sur Kafka", ["source_flux"]
)

API_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"
API_COLUMNS = [
    "numero_dpe", "code_insee_ban", "date_reception_dpe",
    "etiquette_dpe", "etiquette_ges", "surface_habitable_logement",
]


def make_producer():
    for attempt in range(20):
        try:
            return KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        except Exception as e:
            print(f"[producer] Kafka indisponible ({e}), retry {attempt + 1}/20...")
            time.sleep(3)
    raise RuntimeError("Impossible de se connecter à Kafka")


def backfill(producer):
    if os.path.exists(BACKFILL_DONE_FILE):
        print("[producer] backfill déjà effectué lors d'un précédent démarrage, on saute cette phase")
        return
    if not os.path.exists(BACKFILL_CSV):
        print(f"[producer] pas de fichier de backfill ({BACKFILL_CSV}), on saute cette phase")
        return
    print(f"[producer] backfill depuis {BACKFILL_CSV} (~{BACKFILL_RATE}/s)")
    sent = 0
    delay = 1.0 / BACKFILL_RATE if BACKFILL_RATE > 0 else 0
    with open(BACKFILL_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            event = {
                "numero_dpe": row.get("numero_dpe"),
                "code_insee": row.get("code_insee"),
                "date_reception_dpe": row.get("date_etablissement_dpe"),
                "etiquette_dpe": row.get("etiquette_dpe"),
                "etiquette_ges": row.get("etiquette_ges"),
                "surface_habitable_logement": row.get("surface_habitable_logement"),
                "source_flux": "backfill",
            }
            producer.send(TOPIC, event)
            EVENTS_PUBLISHED.labels(source_flux="backfill").inc()
            sent += 1
            if sent % 2000 == 0:
                print(f"[producer] backfill : {sent} événements envoyés")
            if delay:
                time.sleep(delay)
    producer.flush()
    os.makedirs(os.path.dirname(BACKFILL_DONE_FILE), exist_ok=True)
    with open(BACKFILL_DONE_FILE, "w") as f:
        f.write(str(sent))
    print(f"[producer] backfill terminé : {sent} événements")


def load_watermark():
    if os.path.exists(WATERMARK_FILE):
        with open(WATERMARK_FILE) as f:
            return f.read().strip() or None
    return None


def save_watermark(value):
    os.makedirs(os.path.dirname(WATERMARK_FILE), exist_ok=True)
    with open(WATERMARK_FILE, "w") as f:
        f.write(value)


def fetch_new_dpe(since):
    qs = f"code_departement_ban:{DEPARTEMENT}"
    if since:
        qs += f' AND date_reception_dpe:[{since} TO *]'
    params = {
        "qs": qs,
        "select": ",".join(API_COLUMNS),
        "sort": "date_reception_dpe",
        "size": "1000",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "tp2-audit-44/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8")).get("results", [])


def live_poll(producer):
    since = load_watermark()
    print(f"[producer] passage en mode live (watermark = {since})")
    while True:
        try:
            rows = fetch_new_dpe(since)
        except Exception as e:
            print(f"[producer] erreur API ADEME : {e}")
            rows = []
        for row in rows:
            event = {
                "numero_dpe": row.get("numero_dpe"),
                "code_insee": row.get("code_insee_ban"),
                "date_reception_dpe": row.get("date_reception_dpe"),
                "etiquette_dpe": row.get("etiquette_dpe"),
                "etiquette_ges": row.get("etiquette_ges"),
                "surface_habitable_logement": row.get("surface_habitable_logement"),
                "source_flux": "live",
            }
            producer.send(TOPIC, event)
            EVENTS_PUBLISHED.labels(source_flux="live").inc()
            if row.get("date_reception_dpe"):
                since = row["date_reception_dpe"]
        if rows:
            producer.flush()
            save_watermark(since)
            print(f"[producer] live : {len(rows)} nouveaux DPE publiés (watermark = {since})")
        else:
            print("[producer] live : aucun nouveau DPE ce cycle")
        time.sleep(POLL_INTERVAL)


def main():
    start_http_server(METRICS_PORT)
    producer = make_producer()
    backfill(producer)
    live_poll(producer)


if __name__ == "__main__":
    main()
