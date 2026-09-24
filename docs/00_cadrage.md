# Étape 1 — Cadrage et choix du sujet

> Note sur l'énoncé : `tp_bdd.pdf` (à la racine du dépôt) est un export web tronqué — une seule page, le texte s'arrête net après "Format : CSV, Excel, JSON, SQL, etc.". Les sections au-delà de "2. Identifier les sources" (nature/structure des données, modélisation, livrables, critères d'évaluation) ne sont pas présentes dans le fichier. À re-exporter depuis Nowledgeable si besoin de les vérifier — la suite de cette documentation part de l'objectif énoncé : passer de données réelles à une modélisation structurée, puis à une base PostgreSQL.

## Sujet retenu

**Immobilier × Énergie — Performance énergétique et marché immobilier des logements en Loire-Atlantique (44)**

Plutôt que de traiter "immobilier" ou "énergie" isolément, on croise les deux : pour les communes du département 44, on rapproche les **transactions immobilières** (DVF) et les **diagnostics de performance énergétique** (DPE) des logements. Ça permet des questions concrètes type *"un logement mal classé (F/G) se vend-il moins cher au m² ?"* ou *"quelles communes du 44 cumulent un parc énergivore et des prix élevés ?"*.

**Pourquoi ce choix :**
- Couvre les deux pistes envisagées avec le binôme (immobilier + énergie) sans disperser l'effort sur deux sujets séparés.
- Jeux de données réels, ouverts, mis à jour régulièrement, et bien documentés (contrairement à beaucoup d'entrées data.gouv.fr qui sont juste des redirections vers un portail source).
- Modélisation relationnelle naturelle pour l'exercice SQL : plusieurs entités factuelles (transactions, diagnostics) reliées à une dimension géographique commune (commune/INSEE), adaptée à un MCD → MPD → PostgreSQL.

## Périmètre

**Département retenu : Loire-Atlantique (44)** — décidé avec le binôme.

Le département 44 mêle un pôle urbain dense (Nantes, Saint-Nazaire) et des zones rurales/littorales, ce qui donne une diversité de types de logements et de niveaux de prix intéressante pour l'analyse, tout en gardant une volumétrie raisonnable (dizaines de milliers de transactions/diagnostics, pas des millions).

## Répartition du travail avec le binôme

À définir — suggestion : un binôme prend en charge le pipeline DVF (import + audit + modèle), l'autre le pipeline DPE, la jointure géographique (COG) et le rapprochement final étant fait à deux.

## Sommaire de la documentation

1. [00_cadrage.md](00_cadrage.md) — ce document
2. [01_sources.md](01_sources.md) — sources de données identifiées et documentées
3. [02_audit_qualite.md](02_audit_qualite.md) — méthodologie d'audit de la qualité des données
4. [03_modelisation.md](03_modelisation.md) — MCD / MPD
5. [04_base_postgresql.md](04_base_postgresql.md) — création de la base PostgreSQL et import
