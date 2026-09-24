# 1. Présentation du sujet

## Contexte

La rénovation énergétique et la valeur des biens immobiliers sont deux enjeux étroitement liés en France : depuis 2021, le Diagnostic de Performance Énergétique (DPE) est opposable et influence de plus en plus la décision d'achat, tandis que les données de transactions immobilières (DVF) permettent d'objectiver les prix du marché. Croiser ces deux sources à l'échelle d'un département permet de sortir du discours général et d'observer, sur des données réelles, le lien entre performance énergétique et marché immobilier local.

## Problématique

Dans le département de la **Loire-Atlantique (44)**, existe-t-il un écart de prix observable entre les logements performants (étiquettes DPE A/B/C) et les logements énergivores (étiquettes F/G), et comment cet écart varie-t-il selon les communes ?

## Objectif

Construire, à partir de trois jeux de données publics réels, une base de données PostgreSQL structurée permettant :
- de rapprocher transactions immobilières et diagnostics énergétiques à l'échelle communale,
- de cartographier les communes du département selon le niveau de prix et la performance énergétique du parc de logements,
- de servir de support à des requêtes d'analyse (prix moyen au m² par étiquette DPE, par commune, etc.).

## Sujet retenu

**Immobilier × Énergie** — croisement de deux sujets de la liste plutôt qu'un seul, pour donner du sens à l'analyse (un jeu de données immobilier seul ne dit rien sur l'énergie, et inversement).

## Périmètre

**Département : Loire-Atlantique (44)**, 207 communes. Choix motivé par un équilibre entre pôle urbain dense (Nantes, Saint-Nazaire) et zones rurales/littorales, offrant une diversité de types de logements et de niveaux de prix, avec une volumétrie de données maîtrisable pour un TP (dizaines à centaines de milliers de lignes, pas de traitement à l'échelle nationale).

## Répartition du travail avec le binôme

À définir en interne — suggestion : un binôme prend en charge le pipeline DVF, l'autre le pipeline DPE, la jointure géographique (COG) et le rapprochement final étant fait à deux.

## Sommaire de la documentation

1. [01_presentation_sujet.md](01_presentation_sujet.md) — ce document
2. [02_sources.md](02_sources.md) — sources de données
3. [03_dictionnaire_donnees.md](03_dictionnaire_donnees.md) — dictionnaire de données
4. [04_modele_conceptuel.md](04_modele_conceptuel.md) — modèle conceptuel (MCD)
5. [05_modele_logique.md](05_modele_logique.md) — modèle logique (MLD)
6. [06_base_postgresql.md](06_base_postgresql.md) — base PostgreSQL
7. [07_cartographie_globale.md](07_cartographie_globale.md) — cartographie globale du cheminement
8. [annexe_audit_qualite.md](annexe_audit_qualite.md) — audit de qualité des données (travail préparatoire)
