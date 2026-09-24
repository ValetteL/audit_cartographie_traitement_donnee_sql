# Étape 5 — Base PostgreSQL

> À compléter une fois le MPD ([03_modelisation.md](03_modelisation.md)) validé.

## Plan

1. Créer la base PostgreSQL du projet (nom à définir, ex. `audit_immo_energie_44`).
2. Écrire les scripts DDL (`sql/01_create_tables.sql`) pour les tables `commune`, `transaction`, `diagnostic_dpe`.
3. Importer les CSV du département 44 (`data/`) via `COPY` ou un script Python (pandas + psycopg2/SQLAlchemy) dans des tables de staging, puis transformer vers les tables finales.
4. Écrire des requêtes de contrôle post-import (comptages, contrôle des FK, doublons).
5. Écrire les requêtes d'analyse répondant aux questions du cadrage (prix moyen au m² par étiquette DPE et par commune, cartographie des communes energivores vs prix élevés).

## Scripts

- `sql/01_create_tables.sql` — DDL (à créer)
- `sql/02_import.sql` ou script Python d'import (à créer)
- `sql/03_requetes_analyse.sql` — requêtes finales (à créer)

*(sections à compléter au fur et à mesure de l'avancement)*
