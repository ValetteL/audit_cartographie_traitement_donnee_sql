"""Télécharge les diagnostics DPE (ADEME) pour un département, via l'API data-fair.

Usage (depuis la racine du projet) : python scripts/telecharger_dpe.py
Sortie : data/dpe_44.csv
"""
import csv
import json
import time
import urllib.parse
import urllib.request

DEPARTEMENT = "44"
BASE_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"
COLONNES = [
    "numero_dpe", "code_insee_ban", "code_postal_ban", "date_etablissement_dpe",
    "etiquette_dpe", "etiquette_ges", "annee_construction", "periode_construction",
    "type_batiment", "surface_habitable_logement", "adresse_ban",
]
SORTIE = f"data/dpe_{DEPARTEMENT}.csv"


def main():
    params = {
        "qs": f"code_departement_ban:{DEPARTEMENT}",
        "select": ",".join(COLONNES),
        "size": "10000",
    }
    url = BASE_URL + "?" + urllib.parse.urlencode(params)

    total_written = 0
    total_count = None

    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES)
        writer.writeheader()
        page = 0
        while url:
            page += 1
            req = urllib.request.Request(url, headers={"User-Agent": "tp-audit-44/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if total_count is None:
                total_count = data.get("total")
                print(f"total à récupérer : {total_count}")
            results = data.get("results", [])
            for row in results:
                writer.writerow({c: row.get(c, "") for c in COLONNES})
            total_written += len(results)
            print(f"page {page} : +{len(results)} lignes (cumul {total_written}/{total_count})")
            url = data.get("next")
            if not results:
                break
            time.sleep(0.3)

    print(f"Terminé. {total_written} lignes écrites dans {SORTIE}")


if __name__ == "__main__":
    main()
