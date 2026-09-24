# 3. Dictionnaire de données

Analyse des principales colonnes retenues pour chaque source, restreintes au département 44. Seules les colonnes utiles au modèle sont détaillées (les fichiers sources bruts contiennent davantage de colonnes — 38 pour DVF, 230 pour le DPE).

## DVF — transactions immobilières

| Champ | Description | Type | Exemple |
|---|---|---|---|
| `id_mutation` | Identifiant de la mutation (peut se répéter sur plusieurs lignes si plusieurs lots/parcelles) | varchar | `2025-563764` |
| `date_mutation` | Date de la transaction | date | `2025-01-06` |
| `nature_mutation` | Type de mutation | varchar | `Vente` |
| `valeur_fonciere` | Prix de la transaction en euros | numeric | `175000` |
| `code_postal` | Code postal du bien | char(5) | `44520` |
| `code_commune` | Code INSEE de la commune | char(5) | `44099` |
| `nom_commune` | Nom de la commune | varchar | `Moisdon-la-Rivière` |
| `code_departement` | Code département | char(2) | `44` |
| `id_parcelle` | Identifiant cadastral de la parcelle | varchar | `44099000AC0006` |
| `code_type_local` | Code du type de local | integer | `1` |
| `type_local` | Type de bien | varchar | `Maison`, `Appartement` |
| `surface_reelle_bati` | Surface bâtie en m² | numeric | `98` |
| `nombre_pieces_principales` | Nombre de pièces | integer | `5` |
| `surface_terrain` | Surface du terrain en m² | numeric | `945` |
| `longitude` / `latitude` | Coordonnées géographiques | numeric | `-1.37258` / `47.624643` |

## DPE — diagnostics de performance énergétique

| Champ | Description | Type | Exemple |
|---|---|---|---|
| `numero_dpe` | Identifiant unique du diagnostic | varchar | `2644E0039039K` |
| `code_insee_ban` | Code INSEE de la commune (géocodage BAN) | char(5) | `44109` |
| `code_postal_ban` | Code postal (géocodage BAN) | char(5) | `44300` |
| `date_etablissement_dpe` | Date de réalisation du diagnostic | date | `2026-01-07` |
| `etiquette_dpe` | Étiquette énergie (A à G) | char(1) | `C` |
| `etiquette_ges` | Étiquette gaz à effet de serre (A à G) | char(1) | `C` |
| `annee_construction` | Année de construction du bâtiment | integer | `2020` |
| `periode_construction` | Tranche de période de construction | varchar | `2013-2021` |
| `type_batiment` | Type de bâtiment | varchar | `appartement`, `maison` |
| `surface_habitable_logement` | Surface habitable en m² | numeric | `64.3` |
| `adresse_ban` | Adresse complète normalisée (BAN) | varchar | `20 Route de Carquefou 44300 Nantes` |

## COG — communes (référentiel géographique)

| Champ | Description | Type | Exemple |
|---|---|---|---|
| `code_insee` | Code INSEE de la commune (clé primaire) | char(5) | `44109` |
| `nom_standard` | Nom usuel de la commune | varchar | `Nantes` |
| `dep_code` | Code département | char(2) | `44` |
| `dep_nom` | Nom du département | varchar | `Loire-Atlantique` |
| `reg_code` | Code région | char(2) | `52` |
| `reg_nom` | Nom de la région | varchar | `Pays de la Loire` |
| `code_postal` | Code postal principal | char(5) | `44000` |
| `epci_code` / `epci_nom` | Identifiant / nom de l'intercommunalité | varchar | `244400404` / `Nantes Métropole` |

## Clé de rapprochement entre les sources

Les trois sources partagent un **code INSEE de commune à 5 caractères** :
- DVF : `code_commune`
- DPE : `code_insee_ban`
- COG : `code_insee`

C'est la clé utilisée pour la jointure géographique dans le modèle (cf. [04_modele_conceptuel.md](04_modele_conceptuel.md)).
