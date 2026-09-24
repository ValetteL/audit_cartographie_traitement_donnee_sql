# Étape 2 — Identifier les sources

Pour chaque source : nom, organisation/origine, URL, format, nature et modalité d'accès pour le périmètre retenu (département 44).

## Sources principales

### 1. DVF — Demandes de valeurs foncières (géolocalisée)

| Champ | Valeur |
|---|---|
| Nom de la source | DVF géolocalisée (geo-dvf) |
| Organisation / origine | DGFiP, republié/enrichi par Etalab (mission Etalab / datagouv) |
| URL fiche | https://www.data.gouv.fr/datasets/demande-de-valeurs-foncieres-geolocalisee-1 |
| URL téléchargement direct (dépt. 44) | https://files.data.gouv.fr/geo-dvf/latest/csv/2025/departements/44.csv.gz |
| Format | CSV compressé (.csv.gz) |
| Nature | Transactions immobilières réelles (mutations foncières), géolocalisées, historique glissant ~5 ans, mise à jour ~2×/an |
| Licence | Licence Ouverte / Etalab |

Le dépôt GitHub [datagouv/dvf](https://github.com/datagouv/dvf) documente le schéma des colonnes et les scripts de génération de ces exports par département — à consulter pour le dictionnaire de données.

### 2. DPE Logements existants (depuis juillet 2021)

| Champ | Valeur |
|---|---|
| Nom de la source | DPE Logements existants |
| Organisation / origine | ADEME — Observatoire DPE-Audit |
| URL fiche | https://data.ademe.fr/datasets/dpe03existant |
| Accès filtré département 44 | Via la vue tableau du portail : ouvrir le jeu de données → icône "vue tableau" → filtrer sur `code_departement_ban = 44` (ou champ équivalent, à confirmer dans le dictionnaire des champs) → exporter en CSV. Une API REST (data-fair) et un export PostgreSQL complet existent aussi, cf. section "Accès API" du portail. |
| Format | CSV (export filtré) ou API REST / dump PostgreSQL (jeu complet France) |
| Nature | Diagnostics de performance énergétique individuels (par logement), ~15,5M d'enregistrements au niveau national, mise à jour hebdomadaire |
| Licence | Licence Ouverte / Etalab |

⚠️ Le nom exact du champ département n'est pas encore confirmé (à vérifier dans le dictionnaire technique du jeu de données, lien "Documentation" sur la page). Étape à faire lors du téléchargement effectif.

### 3. Code Officiel Géographique (COG) — communes

| Champ | Valeur |
|---|---|
| Nom de la source | Liste des communes de France (COG) |
| Organisation / origine | INSEE, republié via data.gouv.fr |
| URL | https://www.data.gouv.fr/datasets/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather |
| Format | CSV / Excel / JSON / Parquet |
| Nature | Table de référence géographique (code INSEE, codes postaux, département, région, population, superficie), mise à jour annuelle |
| Filtrage 44 | Filtrer les lignes où `departement = 44` après téléchargement (fichier national léger, pas besoin d'export pré-filtré) |
| Licence | Licence Ouverte / Etalab |

## Sources optionnelles (enrichissement ou repli "100% énergie")

| Nom de la source | Organisation / origine | URL | Format | Nature |
|---|---|---|---|---|
| Consommation électrique annuelle par commune et secteur d'activité | Enedis | https://data.enedis.fr/explore/dataset/consommation-electrique-par-secteur-dactivite-commune/ | CSV / API Opendatasoft | Agrégats annuels 2011–2024, maille commune, filtrable par département |
| Données éCO2mix régionales consolidées | RTE — Open Data Réseaux Énergies (ODRÉ) | https://odre.opendatasoft.com/explore/dataset/eco2mix-regional-cons-def/ | CSV / API | Production/consommation régionale (Pays de la Loire pour le 44), pas demi-horaire, historique depuis 2021 |

## Remarque sur data.gouv.fr

Conservé pour le COG (fiche officielle et stable), mais pour DVF et DPE on pointe directement vers les portails sources qui font autorité (respectivement `files.data.gouv.fr/geo-dvf` et `data.ademe.fr`) — data.gouv.fr référence souvent ces mêmes jeux mais avec moins de granularité/documentation que le portail d'origine.
