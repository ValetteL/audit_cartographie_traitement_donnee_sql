#!/usr/bin/env bash
# Télécharge les 3 sources brutes pour le département 44 (cf. docs/02_sources.md).
# À exécuter depuis la racine du projet : bash scripts/telecharger_donnees.sh
set -euo pipefail

DEPT="44"
mkdir -p data

echo "-- DVF (geo-dvf, DGFiP/Etalab) --"
curl -sL -o "data/dvf_${DEPT}_2025.csv.gz" \
  "https://files.data.gouv.fr/geo-dvf/latest/csv/2025/departements/${DEPT}.csv.gz"

echo "-- DPE (ADEME, API data-fair, paginé) --"
python3 scripts/telecharger_dpe.py

echo "-- COG (INSEE, via data.gouv.fr) --"
curl -sL -o /tmp/cog_communes_france.csv \
  "https://www.data.gouv.fr/api/1/datasets/r/c63fd0b1-7987-46f6-b779-8b3ed889090c"
python3 -c "
import csv
with open('/tmp/cog_communes_france.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = [r for r in reader if r['dep_code'] == '${DEPT}']
    fieldnames = reader.fieldnames
with open('data/cog_communes_${DEPT}.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
print(f'{len(rows)} communes écrites dans data/cog_communes_${DEPT}.csv')
"

echo "Terminé. Prochaine étape : python3 scripts/nettoyer_donnees.py"
