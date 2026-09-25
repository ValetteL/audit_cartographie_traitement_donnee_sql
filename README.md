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

## Démarrage rapide

```bash
docker compose up -d
```

Crée la base PostgreSQL, les tables et importe les données réelles du département 44 (207 communes, 79 315 transactions, 351 959 diagnostics) — sans étape manuelle ni accès réseau, les CSV nettoyés sont versionnés dans `data/staging/`. Détails et méthode alternative sans docker compose : [docs/06_base_postgresql.md](docs/06_base_postgresql.md).

## Structure du dépôt

```
docs/            documentation de chaque livrable
data/            extraits bruts (non versionnés) et data/staging/ (nettoyés, versionnés)
scripts/         téléchargement et nettoyage des sources, pour régénérer data/staging/
sql/             scripts DDL, import, requêtes de vérification et d'analyse
rendu/           rapport final assemblé (PDF et HTML) — le document à soumettre
docker-compose.yml   base PostgreSQL prête à l'emploi (voir Démarrage rapide)
```
