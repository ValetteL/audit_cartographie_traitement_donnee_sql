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

Sur les données réelles, le croisement prix moyen au m² / part de logements F-G par commune (`sql/05_requetes_analyse.sql`, requête 3) fait apparaître une tendance : les communes les plus chères et les plus urbaines/littorales (Nantes 8 677 €/m² et 5,4 % de F-G, Saint-Herblain 4 108 €/m² et 3,0 %, Orvault 3 392 €/m² et 3,5 %) ont proportionnellement moins de logements énergivores que les communes rurales les moins chères (Juigné-des-Moutiers 1 078 €/m² et 35,7 % de F-G, Soulvache 1 001 €/m² et 25,7 %, Grand-Auverné 1 307 €/m² et 20,4 %).

Cette observation va dans le sens de la problématique posée ([01_presentation_sujet.md](01_presentation_sujet.md)) mais reste à nuancer : petites communes rurales = faibles effectifs (parfois <30 ventes), et un parc ancien plus présent en zone rurale peut expliquer à la fois le prix bas et la mauvaise étiquette, sans lien de causalité direct entre les deux. Une valeur aberrante (Saint-Philbert-de-Grand-Lieu, 26 644 €/m²) a par ailleurs été identifiée et documentée dans l'annexe qualité — à traiter avant toute cartographie définitive.
