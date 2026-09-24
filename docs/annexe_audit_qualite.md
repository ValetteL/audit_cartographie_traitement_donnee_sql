# Annexe — Audit de la qualité des données

Travail préparatoire (pas un livrable en soi), mené une fois le dictionnaire de données ([03_dictionnaire_donnees.md](03_dictionnaire_donnees.md)) et le modèle ([04_modele_conceptuel.md](04_modele_conceptuel.md), [05_modele_logique.md](05_modele_logique.md)) figés — la structure cible est définie en amont à partir de l'analyse des colonnes réelles, puis les données brutes sont nettoyées et filtrées pour correspondre à ce modèle, plutôt que l'inverse. Réalisé avec un script Python (pandas) qui nettoie les trois extraits bruts et produit les fichiers prêts à l'import dans `data/staging/`.

## Résultats par source

### COG (référentiel communes)

- 207 lignes brutes, 207 après nettoyage.
- Aucun doublon de `code_insee`, aucune valeur manquante sur la clé.
- Confirme le nombre officiel de communes de Loire-Atlantique (207).

### DVF (transactions)

- 79 949 lignes brutes → **79 315 lignes retenues**.
- 634 lignes sans `valeur_fonciere` exploitable, retirées (transactions sans prix renseigné, ex. certaines expropriations).
- 53 205 lignes sans `surface_reelle_bati` : normal, une partie des mutations DVF concerne des terrains non bâtis (pas une anomalie, mais un point d'attention pour les requêtes d'analyse — cf. `sql/05_requetes_analyse.sql` qui filtre sur `type_local IN ('Maison','Appartement')` et `surface_reelle_bati > 0`).
- Répartition de `nature_mutation` : très majoritairement des ventes classiques (75 243 sur 79 949), le reste = ventes en VEFA, échanges, adjudications.
- Répartition de `type_local` : beaucoup de lignes "Dépendance" (garages, caves — 21 271) et de lignes sans type (terrains, 31 825), à filtrer selon la question posée.
- 0 ligne avec un `code_insee` hors du référentiel COG 44 — bon signe de cohérence entre les deux sources.

### DPE (diagnostics)

- 351 959 lignes brutes → **351 959 lignes retenues** (aucune ligne perdue).
- 0 doublon sur `numero_dpe`.
- Étiquettes DPE et GES 100 % dans l'ensemble attendu A–G, aucune valeur aberrante.
- 0 ligne avec un `code_insee_ban` hors du référentiel COG 44.
- **Anomalie détectée** : 126 lignes (0,04 %) présentent un artefact d'encodage dans le champ adresse — un caractère accentué mal ré-encodé apparaît littéralement comme une séquence du type `*u00ee` au lieu du caractère attendu (ex. `î`). L'anomalie est présente dès la réponse brute de l'API ADEME, donc en amont de notre traitement — c'est un défaut de qualité de la source, pas de notre pipeline. Volume négligeable, non corrigé (pas bloquant pour l'exploitation en base), mais documenté ici pour traçabilité.

## Anomalie découverte lors des tests SQL

En testant la requête de vérification croisant `transaction_dvf` et `diagnostic_dpe` par commune (`sql/04_requetes_verification.sql`), une première version jointait les deux tables directement sur `commune` dans la même requête. Sur une commune comme Nantes (14 195 transactions × 132 678 diagnostics), cela produit un **produit cartésien** de près de 2 milliards de lignes avant agrégation — requête bloquée en pratique. Corrigé en remplaçant la double jointure par deux sous-requêtes indépendantes (`SELECT COUNT(*) FROM ... WHERE code_insee = c.code_insee`), beaucoup plus efficace et correcte. Bon exemple concret de pourquoi le modèle "étoile" (deux faits reliés uniquement par la dimension commune, jamais entre eux) doit être interrogé prudemment.

## Valeur aberrante corrigée : biais des mutations DVF multi-lots

La première version de la requête de prix moyen au m² par commune (`sql/05_requetes_analyse.sql`, requête 1) faisait ressortir Saint-Philbert-de-Grand-Lieu à 26 644 €/m², très au-dessus de toutes les autres communes (deuxième plus chère à l'époque : Machecoul-Saint-Même à 15 360 €/m², Nantes à 8 677 €/m²).

**Cause identifiée** : dans DVF, une mutation portant sur plusieurs lots (ex. un lotissement de plusieurs maisons vendu par un promoteur en une seule transaction) est éclatée sur plusieurs lignes du fichier source — une ligne par lot — mais `valeur_fonciere` (le prix total de la mutation) est **répété à l'identique sur chaque ligne**, pas réparti. La requête initiale divisait cette valeur totale par la surface de chaque ligne individuellement, ce qui démultiplie artificiellement le prix au m² dès qu'une mutation comporte plusieurs lots.

Exemple concret trouvé sur Saint-Philbert-de-Grand-Lieu : la mutation `2025-583422` (5 591 000 €, vente d'un lotissement) apparaît sur 82 lignes du fichier department 44, chacune avec la même `valeur_fonciere` de 5 591 000 €. Le calcul naïf traitait donc 82 fois cette même vente comme si chaque maison valait individuellement 5,6 M€. Ce n'est pas un cas isolé : sur les 31 633 mutations distinctes du département, 1 877 comportent plus de 5 lignes — le biais affecte donc l'ensemble du classement, pas seulement la commune la plus visible.

**Correction appliquée** : la requête agrège désormais d'abord par `id_mutation` (une valeur foncière par mutation, somme des surfaces des lots `Maison`/`Appartement` de cette mutation), puis calcule le prix au m² sur cette base, avant de moyenner par commune. Résultat : Saint-Philbert-de-Grand-Lieu retombe à 2 347 €/m² (rang médian, cohérent avec ses voisines), et le classement general devient dominé par les communes littorales (La Baule-Escoublac 6 536 €/m², Pornichet 5 647 €/m², Le Pouliguen 5 290 €/m²), un résultat nettement plus plausible pour le marché immobilier du 44. Voir [06_base_postgresql.md](06_base_postgresql.md) pour les chiffres à jour.

## Vérification de bout en bout

Les scripts SQL ont été testés sur une instance PostgreSQL 16 locale (conteneur Docker), avec :

- création des tables (`01_create_tables.sql`) : OK
- insertion des données de test (`02_insert_test_data.sql`) : OK, relations vérifiées (0 ligne orpheline)
- import complet des données réelles nettoyées (`03_import_donnees_reelles.sql`) : OK — 207 communes, 79 315 transactions, 351 959 diagnostics, **0 ligne orpheline**
- requêtes d'analyse (`05_requetes_analyse.sql`) : OK — résultats cohérents avec la problématique (cf. [06_base_postgresql.md](06_base_postgresql.md))
