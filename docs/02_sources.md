# 2. Sources de données

Trois sources réelles, toutes restreintes au département de la Loire-Atlantique (44).

## 1. DVF — Demandes de valeurs foncières (géolocalisée)

| Champ | Valeur |
|---|---|
| Nom de la source | DVF géolocalisée (geo-dvf) |
| Organisation / origine | DGFiP, republiée par Etalab |
| URL | https://files.data.gouv.fr/geo-dvf/latest/csv/2025/departements/44.csv.gz |
| Format | CSV compressé (.csv.gz) |
| Nature | Structurée (une ligne = une disposition de mutation) |
| Description | Transactions immobilières réelles (ventes de maisons, appartements, terrains, locaux) sur le département 44, géolocalisées. |

## 2. DPE Logements existants (depuis juillet 2021)

| Champ | Valeur |
|---|---|
| Nom de la source | DPE Logements existants |
| Organisation / origine | ADEME — Observatoire DPE-Audit |
| URL | https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines |
| Format | JSON via API (data-fair), converti en CSV |
| Nature | Structurée (un enregistrement = un diagnostic) |
| Description | Diagnostics de performance énergétique individuels (par logement) : étiquette énergie, étiquette GES, année de construction, surface habitable, type de bâtiment, adresse. Filtrage sur le département via `qs=code_departement_ban:44`. |

## 3. Code Officiel Géographique (COG) — communes

| Champ | Valeur |
|---|---|
| Nom de la source | Liste des communes de France (COG) |
| Organisation / origine | INSEE, republiée via data.gouv.fr |
| URL | https://www.data.gouv.fr/datasets/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather |
| Format | CSV |
| Nature | Structurée (une ligne = une commune) |
| Description | Table de référence géographique : code INSEE, nom, codes postaux, département, région, EPCI, population. |

Les trois sources sont reliées par le code INSEE de la commune (`code_commune` en DVF, `code_insee_ban` en DPE, `code_insee` en COG).

Téléchargement reproductible : `scripts/telecharger_donnees.sh`. Les CSV nettoyés issus de ces sources (`data/staging/`) sont versionnés dans le dépôt pour que `docker compose up` fonctionne sans dépendre d'un accès réseau — cf. [06_base_postgresql.md](06_base_postgresql.md).
