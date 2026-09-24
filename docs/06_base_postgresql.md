# 6. Base PostgreSQL

## Scripts

| Script | Rôle |
|---|---|
| [sql/01_create_tables.sql](../sql/01_create_tables.sql) | Création des 3 tables, contraintes, index |
| [sql/02_insert_test_data.sql](../sql/02_insert_test_data.sql) | Quelques données de test manuelles (3 communes, 3 transactions, 3 diagnostics) |
| [sql/03_import_donnees_reelles.sql](../sql/03_import_donnees_reelles.sql) | Import des données réelles nettoyées du département 44 (`data/staging/`) |
| [sql/04_requetes_verification.sql](../sql/04_requetes_verification.sql) | Contrôle des relations (comptages, orphelins) |
| [sql/05_requetes_analyse.sql](../sql/05_requetes_analyse.sql) | Requêtes répondant à la problématique du TP |

## Comment reproduire

### Option A — via Docker (utilisée pour valider les scripts)

```bash
docker run -d --name tp_audit_44_pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=audit_immo_energie_44 -p 5433:5432 postgres:16

psql -h localhost -p 5433 -U postgres -d audit_immo_energie_44 -f sql/01_create_tables.sql
psql -h localhost -p 5433 -U postgres -d audit_immo_energie_44 -f sql/02_insert_test_data.sql   # données de test
# ou, pour les données réelles (depuis la racine du projet, où se trouve data/staging/) :
psql -h localhost -p 5433 -U postgres -d audit_immo_energie_44 -f sql/03_import_donnees_reelles.sql
```

### Option B — via pgAdmin

1. Créer une base `audit_immo_energie_44`.
2. Ouvrir le Query Tool, exécuter `01_create_tables.sql`.
3. Exécuter `02_insert_test_data.sql` pour les données de test, ou importer les CSV de `data/staging/` via l'outil d'import graphique de pgAdmin pour les données réelles.

## Résultats de la vérification (exécutée le 24/09/2026)

Base créée et testée sur une instance PostgreSQL 16 locale (Docker), avec import complet des trois sources nettoyées (cf. [annexe_audit_qualite.md](annexe_audit_qualite.md)) :

| Table | Lignes importées |
|---|---|
| commune | 207 |
| transaction_dvf | 79 315 |
| diagnostic_dpe | 351 959 |

- **0 transaction orpheline**, **0 diagnostic orphelin** : toutes les clés étrangères vers `commune` sont valides.
- Les contraintes CHECK (étiquettes DPE/GES dans A–G, surfaces et prix ≥ 0) sont passées sans erreur sur l'ensemble du jeu réel.

## Résultat des requêtes d'analyse

Le prix moyen au m² est calculé au niveau de la mutation (et non de la ligne brute) pour éviter un biais des mutations DVF à plusieurs lots — cf. [annexe_audit_qualite.md](annexe_audit_qualite.md) pour le détail du problème rencontré et de la correction apportée.

Sur les données réelles corrigées, le croisement prix moyen au m² / part de logements F-G par commune (`sql/05_requetes_analyse.sql`, requête 3) fait apparaître deux tendances :

- Les communes les plus chères du département sont ses pôles littoraux (La Baule-Escoublac 6 536 €/m², Pornichet 5 647 €/m², Le Pouliguen 5 290 €/m², Pornic 4 840 €/m²), suivies de Nantes (3 778 €/m², rang médian malgré son statut de préfecture) et de sa périphérie (Saint-Herblain 2 793 €/m², Orvault 3 177 €/m²).
- Les communes rurales les moins chères concentrent la plus forte part de logements F-G : Juigné-des-Moutiers (892 €/m², 35,7 % de F-G), La Chapelle-Glain (921 €/m², 19,4 %), Soulvache (1 015 €/m², 25,7 %), Grand-Auverné (1 102 €/m², 20,4 %).

Cette observation va dans le sens de la problématique posée ([01_presentation_sujet.md](01_presentation_sujet.md)) mais reste à nuancer : les communes rurales les moins chères ont de faibles effectifs (souvent 10 à 20 mutations), et un parc ancien plus présent en zone rurale peut expliquer à la fois le prix bas et la mauvaise étiquette, sans lien de causalité direct entre les deux. Le prix des communes littorales, à l'inverse, reflète surtout la rareté foncière (proximité de la mer) plus que la performance énergétique du bâti.
