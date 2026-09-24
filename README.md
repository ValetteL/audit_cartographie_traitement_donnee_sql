# TP — Audit & cartographie des données

Sujet : **Immobilier × Énergie**, performance énergétique et marché immobilier en **Loire-Atlantique (44)**.

Croisement de trois sources ouvertes (DVF, DPE ADEME, COG INSEE) pour passer de données réelles à une modélisation structurée, puis à une base PostgreSQL.

## Rendu

Le document à soumettre est [rendu/rapport_tp.pdf](rendu/rapport_tp.pdf) (version HTML autonome : [rendu/rapport_tp.html](rendu/rapport_tp.html)).

## Livrables

Chaque livrable du TP est documenté dans [docs/](docs/) :

1. [01_presentation_sujet.md](docs/01_presentation_sujet.md) — contexte, problématique, objectif
2. [02_sources.md](docs/02_sources.md) — sources de données : origine, URL, formats, nature
3. [03_dictionnaire_donnees.md](docs/03_dictionnaire_donnees.md) — dictionnaire de données
4. [04_modele_conceptuel.md](docs/04_modele_conceptuel.md) — modèle conceptuel (entités, attributs, relations, cardinalités)
5. [05_modele_logique.md](docs/05_modele_logique.md) — modèle logique (tables, PK, FK)
6. [06_base_postgresql.md](docs/06_base_postgresql.md) — base PostgreSQL : scripts et résultats de vérification
7. [07_cartographie_globale.md](docs/07_cartographie_globale.md) — vue d'ensemble du cheminement

## Structure du dépôt

```
docs/    documentation de chaque livrable
data/    extraits bruts et nettoyés (département 44) — non versionnés (cf. .gitignore)
sql/     scripts DDL, import, requêtes de vérification et d'analyse
rendu/   rapport final assemblé (PDF et HTML) — le document à soumettre
```

## Reproduire

```bash
# 1. Récupérer les données du département 44 (cf. docs/02_sources.md pour le détail des sources)
# 2. Nettoyer/filtrer -> data/staging/
# 3. Créer la base et importer
psql -d audit_immo_energie_44 -f sql/01_create_tables.sql
psql -d audit_immo_energie_44 -f sql/03_import_donnees_reelles.sql   # ou 02_insert_test_data.sql pour un jeu de test
psql -d audit_immo_energie_44 -f sql/04_requetes_verification.sql
psql -d audit_immo_energie_44 -f sql/05_requetes_analyse.sql
```

Détails complets dans [docs/06_base_postgresql.md](docs/06_base_postgresql.md).
