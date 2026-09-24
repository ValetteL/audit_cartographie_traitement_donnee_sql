# 1. Présentation du sujet

## Contexte

La rénovation énergétique et la valeur des biens immobiliers sont deux enjeux étroitement liés en France : depuis 2021 le Diagnostic de Performance Énergétique (DPE) influence la décision d'achat, tandis que les données de transactions immobilières (DVF) objectivent les prix du marché. Croiser ces deux sources à l'échelle d'un département permet d'observer, sur des données réelles, le lien entre performance énergétique et marché immobilier local.

## Problématique

Dans le département de la **Loire-Atlantique (44)**, existe-t-il un écart de prix observable entre les logements performants (étiquettes DPE A/B/C) et les logements énergivores (étiquettes F/G), et comment cet écart varie-t-il selon les communes ?

## Objectif

Construire, à partir de trois jeux de données publics réels, une base de données PostgreSQL structurée permettant de rapprocher transactions immobilières et diagnostics énergétiques à l'échelle communale, et de répondre à la problématique par des requêtes d'analyse (prix moyen au m² par étiquette DPE, par commune).

## Sujet retenu

**Immobilier × Énergie** — croisement de deux sujets de la liste plutôt qu'un seul, pour donner du sens à l'analyse.

## Périmètre

**Département : Loire-Atlantique (44)**, 207 communes — équilibre entre pôle urbain (Nantes, Saint-Nazaire) et zones rurales/littorales, avec une volumétrie maîtrisable pour un TP.
