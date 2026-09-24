# Étape 4 — Modélisation (MCD / MPD)

> Ébauche à affiner après l'audit qualité ([02_audit_qualite.md](02_audit_qualite.md)) — les types de colonnes et clés définitives dépendent de la structure réelle observée sur les extraits du 44.

## Entités pressenties (MCD)

- **Commune** (`code_insee` PK, nom, code_postal, departement, region, population, superficie) — table de dimension, issue du COG, restreinte au département 44.
- **Transaction** (`id` PK, `code_insee` FK → Commune, date_mutation, valeur_fonciere, surface_reelle_bati, nb_pieces_principales, type_local, section_cadastrale) — issue de DVF.
- **Diagnostic_DPE** (`id` PK, `code_insee` FK → Commune, date_etablissement_dpe, etiquette_dpe, etiquette_ges, annee_construction, surface_habitable, type_batiment) — issue de DPE.

## Relations

`Transaction` et `Diagnostic_DPE` sont toutes deux en 1-N vers `Commune`. Un rapprochement fin transaction ↔ diagnostic (même bien) est possible via l'adresse mais complexe (pas de clé commune fiable entre les deux sources) — pour le TP, un rapprochement **au niveau commune** (agrégats : prix moyen au m² vs répartition des étiquettes DPE) est le point de départ retenu, avec un rapprochement adresse-à-adresse comme piste d'approfondissement si le temps le permet.

## MPD (modèle physique) — à dériver

Une fois le MCD validé, dériver :
- les types PostgreSQL précis par colonne (`numeric`, `date`, `varchar(n)`, `char(5)` pour les codes INSEE, etc.),
- les contraintes (NOT NULL, CHECK sur les étiquettes DPE A–G, FK avec ON DELETE/UPDATE),
- les index utiles (sur `code_insee`, dates de mutation/diagnostic).

*(schéma détaillé et diagramme à ajouter ici une fois le MCD validé avec le binôme)*
