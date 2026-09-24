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

```bash
docker run -d --name tp_audit_44_pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=audit_immo_energie_44 -p 5433:5432 postgres:16

psql -h localhost -p 5433 -U postgres -d audit_immo_energie_44 -f sql/01_create_tables.sql
psql -h localhost -p 5433 -U postgres -d audit_immo_energie_44 -f sql/02_insert_test_data.sql   # données de test
# ou, pour les données réelles (depuis la racine du projet) :
psql -h localhost -p 5433 -U postgres -d audit_immo_energie_44 -f sql/03_import_donnees_reelles.sql
```

## Résultats de la vérification

Base testée avec import complet des trois sources nettoyées :

| Table | Lignes importées |
|---|---|
| commune | 207 |
| transaction_dvf | 79 315 |
| diagnostic_dpe | 351 959 |

**0 transaction orpheline**, **0 diagnostic orphelin** : toutes les clés étrangères sont valides, les contraintes CHECK passent sans erreur.

## Résultat des requêtes d'analyse

Le prix moyen au m² est calculé au niveau de la mutation, pas de la ligne brute, pour éviter un biais des mutations DVF à plusieurs lots (`valeur_fonciere` répétée sur chaque lot) — cf. commentaire en tête de `sql/05_requetes_analyse.sql`.

Le croisement prix moyen au m² / part de logements F-G par commune fait apparaître une tendance : les communes les plus chères sont les pôles littoraux (La Baule-Escoublac 6 536 €/m², Pornichet 5 647 €/m²) et Nantes (3 778 €/m²), avec une part de logements F-G plus faible que les communes rurales les moins chères (Juigné-des-Moutiers 892 €/m² et 35,7 % de F-G, Soulvache 1 015 €/m² et 25,7 %). À nuancer : faibles effectifs sur les petites communes rurales, corrélation ≠ causalité.
