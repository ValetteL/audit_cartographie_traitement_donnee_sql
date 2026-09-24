# Étape 3 — Audit de la qualité des données

> Ce document est un canevas méthodologique. Il est à compléter avec les résultats réels une fois les extraits du département 44 téléchargés dans [data/](../data/).

## Objectif

Avant de figer le modèle relationnel, vérifier pour chaque source :
- la structure réelle des colonnes (types, formats de date, encodage),
- la complétude (valeurs manquantes, taux par colonne clé),
- les doublons,
- la cohérence des clés de jointure (codes INSEE communs aux 3 sources),
- les valeurs aberrantes (ex. `valeur_fonciere` à 0 ou extrême, surfaces nulles, dates hors plage).

## Pour chaque source

### DVF (44)
- [ ] Nombre de lignes / colonnes réelles après téléchargement
- [ ] Types de biens représentés (`type_local`) et leur répartition
- [ ] Part de lignes avec coordonnées géographiques renseignées
- [ ] Doublons de mutation (une mutation peut apparaître sur plusieurs lignes si plusieurs lots/parcelles)
- [ ] Cohérence du code INSEE commune avec le COG

### DPE (44)
- [ ] Nombre de lignes / colonnes réelles après export filtré
- [ ] Répartition des étiquettes DPE/GES
- [ ] Part de valeurs manquantes sur surface habitable, année de construction
- [ ] Cohérence du code INSEE / code postal avec le COG

### COG (44)
- [ ] Nombre de communes du département 44 (référence de contrôle pour les jointures)
- [ ] Vérifier l'absence de doublons de code INSEE

## Méthode

Scripts d'audit à écrire en Python (pandas) ou directement en SQL après un import brut ("staging") dans PostgreSQL, avant transformation vers le modèle final. Résultats à consigner ici (tableaux de complétude, captures, requêtes de contrôle).

## Résultats

*(à compléter)*
