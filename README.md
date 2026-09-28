# TP — Audit & cartographie des données

Sujet : **Immobilier × Énergie**, performance énergétique et marché immobilier en **Loire-Atlantique (44)**.

Croisement de trois sources ouvertes (DVF, DPE ADEME, COG INSEE) pour passer de données réelles à une modélisation structurée, puis à une base PostgreSQL.

## Rendu

- TP1 : [rendu/rapport_tp.pdf](rendu/rapport_tp.pdf) (version HTML autonome : [rendu/rapport_tp.html](rendu/rapport_tp.html))
- TP2 : [rendu/rapport_tp2.pdf](rendu/rapport_tp2.pdf) (version HTML autonome : [rendu/rapport_tp2.html](rendu/rapport_tp2.html))
- TP3 : documentation technique dans [docs/09_tp3_audit_qualite.md](docs/09_tp3_audit_qualite.md) ; support de soutenance orale : [Soutenance TP3 — Audit qualité.pdf](<Soutenance TP3 — Audit qualité.pdf>) et [notes.md](notes.md) (script détaillé, minuté, par diapositive)

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

**TP3 — Audit qualité & nettoyage des données** (prolonge le TP1/TP2) : [09_tp3_audit_qualite.md](docs/09_tp3_audit_qualite.md) — schéma cible vérifié, matrice de contrôles qualité, méthodologie, anomalies identifiées et corrigées, recontrôle avant/après.

## Démarrage rapide

```bash
docker compose up -d
```

Démarre l'ensemble TP1 + TP2 + TP3 : base PostgreSQL avec import des données réelles du département 44 (207 communes, 79 315 transactions, 351 959 diagnostics), corrections d'audit qualité du TP3 déjà appliquées, et le pipeline temps réel (Kafka, data lake, PySpark, PostgreSQL, Prometheus/Grafana pour le monitoring, Metabase pour la dataviz métier) — sans étape manuelle ni accès réseau obligatoire, les CSV nettoyés sont versionnés dans `data/staging/`. Metabase (compte admin, connexion, dashboard) est aussi configuré automatiquement (`admin@tp2.local` / `MetabaseTp2!2026`). Détails : [docs/06_base_postgresql.md](docs/06_base_postgresql.md) (TP1), [docs/08_tp2_pipeline_temps_reel.md](docs/08_tp2_pipeline_temps_reel.md) (TP2, avec les commandes de vérification), [docs/09_tp3_audit_qualite.md](docs/09_tp3_audit_qualite.md) (TP3, audit et corrections).

## Structure du dépôt

```
docs/            documentation de chaque livrable (TP1 : 01-07, TP2 : 08, TP3 : 09)
data/            extraits bruts (non versionnés) et data/staging/ (nettoyés, versionnés)
scripts/         téléchargement et nettoyage des sources, pour régénérer data/staging/
sql/             scripts DDL, import, requêtes de vérification/analyse (TP1), table flux temps réel (TP2), audit/nettoyage (TP3)
rendu/           rapports finaux assemblés — les documents à soumettre (TP1, TP2)
api/             producteur Kafka — Source 1 (DPE, TP2)
source2/         chargeur DVF — Source 2 complémentaire (TP2)
spark/           Spark Structured Streaming : consomme Kafka, data lake, nettoyage, PostgreSQL (TP2)
monitoring/      Prometheus, Grafana (monitoring), docker-stats-exporter et Metabase (dataviz, TP2)
docker-compose.yml   stack complète prête à l'emploi (voir Démarrage rapide)
notes.md, Soutenance TP3 — Audit qualité.pdf   support et script de la soutenance orale (TP3)
```
