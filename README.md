# TP — Audit & cartographie des données

Sujet : **Immobilier × Énergie**, performance énergétique et marché immobilier en **Loire-Atlantique (44)**.

Croisement de trois sources ouvertes (DVF, DPE ADEME, COG INSEE) pour passer de données réelles à une modélisation structurée, puis à une base PostgreSQL.

## Rendu

- TP1 : [rendu/rapport_tp.pdf](rendu/rapport_tp.pdf) (version HTML autonome : [rendu/rapport_tp.html](rendu/rapport_tp.html))
- TP2 : [rendu/rapport_tp2.pdf](rendu/rapport_tp2.pdf) (version HTML autonome : [rendu/rapport_tp2.html](rendu/rapport_tp2.html))

## Livrables

Chaque livrable du TP est documenté dans [docs/](docs/) :

1. [01_presentation_sujet.md](docs/01_presentation_sujet.md) — contexte, problématique, objectif
2. [02_sources.md](docs/02_sources.md) — sources de données : origine, URL, formats, nature
3. [03_dictionnaire_donnees.md](docs/03_dictionnaire_donnees.md) — dictionnaire de données
4. [04_modele_conceptuel.md](docs/04_modele_conceptuel.md) — modèle conceptuel (entités, attributs, relations, cardinalités)
5. [05_modele_logique.md](docs/05_modele_logique.md) — modèle logique (tables, PK, FK)
6. [06_base_postgresql.md](docs/06_base_postgresql.md) — base PostgreSQL : scripts et résultats de vérification
7. [07_cartographie_globale.md](docs/07_cartographie_globale.md) — vue d'ensemble du cheminement

**TP2 — Pipeline data temps réel & plateforme data** (prolonge le TP1) : [08_tp2_pipeline_temps_reel.md](docs/08_tp2_pipeline_temps_reel.md) — architecture, sources, data lake, nettoyage PySpark, observabilité Prometheus/Grafana, dataviz, comment vérifier.

## Démarrage rapide

```bash
docker compose up -d
```

Démarre l'ensemble TP1 + TP2 : base PostgreSQL avec import des données réelles du département 44 (207 communes, 79 315 transactions, 351 959 diagnostics), et le pipeline temps réel (Kafka, data lake, PySpark, PostgreSQL, Prometheus/Grafana pour le monitoring, Metabase pour la dataviz métier) — sans étape manuelle ni accès réseau obligatoire, les CSV nettoyés sont versionnés dans `data/staging/` (seule exception : la configuration initiale de Metabase, propre à cet outil). Détails : [docs/06_base_postgresql.md](docs/06_base_postgresql.md) (TP1) et [docs/08_tp2_pipeline_temps_reel.md](docs/08_tp2_pipeline_temps_reel.md) (TP2, avec les commandes de vérification).

## Structure du dépôt

```
docs/            documentation de chaque livrable (TP1 : 01-07, TP2 : 08)
data/            extraits bruts (non versionnés) et data/staging/ (nettoyés, versionnés)
scripts/         téléchargement et nettoyage des sources, pour régénérer data/staging/
sql/             scripts DDL, import, requêtes de vérification et d'analyse (TP1 + TP2)
rendu/           rapports finaux assemblés (PDF et HTML) — les documents à soumettre (TP1 + TP2)
api/             producteur Kafka — Source 1 (DPE, TP2)
source2/         chargeur DVF — Source 2 complémentaire (TP2)
spark/           Spark Structured Streaming : consomme Kafka, data lake, nettoyage, PostgreSQL (TP2)
monitoring/      configuration Prometheus, Grafana (monitoring) et docker-stats-exporter (TP2)
docker-compose.yml   stack complète prête à l'emploi (voir Démarrage rapide)
```
