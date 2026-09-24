# 2. Sources de données

Trois sources réelles, toutes restreintes au département de la Loire-Atlantique (44). Pour chacune : nom, organisation/origine, URL, format, nature, description, et méthode de récupération effectivement utilisée.

## 1. DVF — Demandes de valeurs foncières (géolocalisée)

| Champ | Valeur |
|---|---|
| Nom de la source | DVF géolocalisée (geo-dvf) |
| Organisation / origine | DGFiP, republiée/enrichie par Etalab |
| URL fiche | https://www.data.gouv.fr/datasets/demande-de-valeurs-foncieres-geolocalisee-1 |
| URL fichier utilisé (dépt. 44) | https://files.data.gouv.fr/geo-dvf/latest/csv/2025/departements/44.csv.gz |
| Format | CSV compressé (.csv.gz) |
| Nature | Structurée (fichier tabulaire, une ligne = une disposition de mutation) |
| Description | Transactions immobilières réelles (mutations foncières : ventes de maisons, appartements, terrains, locaux) sur le département 44, géolocalisées, historique glissant. Chaque mutation peut être répartie sur plusieurs lignes (plusieurs lots/parcelles). |
| Licence | Licence Ouverte / Etalab |
| Récupération | Téléchargement direct du CSV compressé du département (`curl`), conservé tel quel dans `data/dvf_44_2025.csv.gz` (non versionné, cf. `.gitignore`) |

Le dépôt GitHub [datagouv/dvf](https://github.com/datagouv/dvf) documente le schéma des colonnes.

## 2. DPE Logements existants (depuis juillet 2021)

| Champ | Valeur |
|---|---|
| Nom de la source | DPE Logements existants |
| Organisation / origine | ADEME — Observatoire DPE-Audit |
| URL fiche | https://data.ademe.fr/datasets/dpe03existant |
| URL API utilisée | https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines |
| Format | JSON via API (data-fair), converti en CSV |
| Nature | Structurée (schéma de 230 champs, un enregistrement = un diagnostic) |
| Description | Diagnostics de performance énergétique individuels (par logement) : étiquette énergie, étiquette GES, année de construction, surface habitable, type de bâtiment, adresse. |
| Licence | Licence Ouverte / Etalab |
| Récupération | Filtrage via le paramètre `qs=code_departement_ban:44` de l'API, pagination par curseur (`next`), export d'une sélection de 11 colonnes pertinentes vers `data/dpe_44.csv` (non versionné). ~352 000 diagnostics sur le département. |

Champ de filtrage département confirmé dans le schéma de l'API : `code_departement_ban`. Champ de jointure commune : `code_insee_ban`.

## 3. Code Officiel Géographique (COG) — communes

| Champ | Valeur |
|---|---|
| Nom de la source | Liste des communes de France (COG) |
| Organisation / origine | INSEE, republiée via data.gouv.fr |
| URL | https://www.data.gouv.fr/datasets/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather |
| Format | CSV |
| Nature | Structurée (une ligne = une commune) |
| Description | Table de référence géographique : code INSEE, nom, codes postaux, département, région, EPCI, population, superficie. |
| Licence | Licence Ouverte / Etalab |
| Récupération | Téléchargement du fichier national puis filtrage sur `dep_code = 44` (207 communes), écrit dans `data/cog_communes_44.csv` (non versionné) |

## Sources optionnelles (non retenues, envisagées en repli "100 % énergie")

| Nom de la source | Organisation / origine | URL | Format | Nature | Description |
|---|---|---|---|---|---|
| Consommation électrique annuelle par commune et secteur d'activité | Enedis | https://data.enedis.fr/explore/dataset/consommation-electrique-par-secteur-dactivite-commune/ | CSV / API Opendatasoft | Structurée | Agrégats annuels 2011–2024 de consommation électrique, maille commune |
| Données éCO2mix régionales consolidées | RTE — Open Data Réseaux Énergies (ODRÉ) | https://odre.opendatasoft.com/explore/dataset/eco2mix-regional-cons-def/ | CSV / API | Structurée | Production/consommation régionale par filière (Pays de la Loire), pas demi-horaire |

## Remarque sur data.gouv.fr

Conservé pour le COG (fiche officielle et stable), mais pour DVF et DPE les données sont récupérées directement depuis les portails sources qui font autorité (respectivement `files.data.gouv.fr/geo-dvf` et `data.ademe.fr`), plus fiables et mieux documentés que les entrées data.gouv.fr qui les référencent.
