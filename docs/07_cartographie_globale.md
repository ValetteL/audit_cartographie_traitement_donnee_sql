# 7. Cartographie globale

Vue d'ensemble du cheminement, des données brutes à la base PostgreSQL. La structure (dictionnaire de données, MCD, MLD) est établie en premier, à partir de l'analyse des colonnes réelles des sources — le nettoyage n'intervient qu'ensuite, pour adapter les données brutes à cette structure cible plutôt que l'inverse.

![Cartographie globale du cheminement](assets/cartographie_globale.png){width=95%}

## Lecture du schéma

1. **Trois sources hétérogènes** (formats et organisations différentes) sont ramenées à un périmètre commun : le département 44.
2. **Le dictionnaire de données et la modélisation** (MCD → MLD) sont établis en premier, directement à partir de l'analyse des colonnes réelles de chaque source, avant tout nettoyage. La modélisation choisit délibérément une architecture "en étoile" simple (deux tables de faits reliées uniquement par la dimension commune) plutôt qu'un rapprochement fin transaction ↔ diagnostic, jugé trop incertain avec les clés disponibles (cf. justification dans [04_modele_conceptuel.md](04_modele_conceptuel.md)).
3. **L'audit qualité et le nettoyage** interviennent ensuite : ils adaptent les données réelles au modèle défini à l'étape précédente (filtrage, valeurs manquantes, doublons, types), en s'appuyant sur une clé géographique commune fiable (`code_insee`).
4. **La base PostgreSQL** matérialise ce modèle et a été testée de bout en bout avec les données réelles nettoyées (0 ligne orpheline).
5. **L'analyse finale** répond à la problématique initiale à l'échelle communale, après correction d'un biais de calcul sur les mutations DVF multi-lots (cf. [annexe_audit_qualite.md](annexe_audit_qualite.md)), avec ses limites restantes documentées (petits effectifs sur les communes rurales, corrélation ≠ causalité).
