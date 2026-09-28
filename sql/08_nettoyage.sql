-- TP3 — Corrections issues de l'audit (sql/07_audit_qualite.sql)
-- Chaque bloc corrige UNE anomalie précise, avec sa justification. Certaines
-- anomalies détectées par l'audit n'ont volontairement AUCUNE correction ici :
-- une décision de ne pas corriger est une décision à part entière, justifiée
-- dans docs/09_tp3_audit_qualite.md plutôt que dans ce script.

-- ============================================================
-- Correction 1 — nombre_pieces_principales = 0 pour un logement habitable
-- ============================================================
-- 46 lignes (Maison/Appartement) à 0 pièce : valeur invalide pour un
-- logement réellement habitable (0 est en revanche normal pour une
-- Dépendance ou un local commercial, non touché ici). On ne connaît pas le
-- vrai nombre de pièces : substitution par NULL plutôt qu'une valeur
-- inventée, pour ne pas fausser de futures moyennes sur ce champ.
UPDATE transaction_dvf
SET nombre_pieces_principales = NULL
WHERE nombre_pieces_principales = 0
  AND type_local IN ('Maison', 'Appartement');

-- ============================================================
-- Correction 2 — surface_habitable_logement invraisemblable pour un
-- "appartement" (probable confusion avec la surface totale de l'immeuble)
-- ============================================================
-- Borne à 400 m² (cf. justification dans sql/07_audit_qualite.sql). Même
-- logique que la correction 1 : on ne peut pas déduire la vraie surface du
-- logement individuel à partir d'une valeur qu'on sait fausse, donc
-- substitution par NULL plutôt qu'une correction inventée.
UPDATE diagnostic_dpe
SET surface_habitable_logement = NULL
WHERE surface_habitable_logement > 400
  AND type_batiment = 'appartement';

-- Répercuté sur diagnostic_dpe_flux (même anomalie, même correction, si les
-- numero_dpe concernés y sont déjà arrivés via le flux temps réel). Contrôle
-- sur la valeur de surface propre à diagnostic_dpe_flux (pas sur l'état déjà
-- corrigé de diagnostic_dpe), pour ne cibler que les lignes réellement
-- concernées par cette anomalie précise — diagnostic_dpe_flux contient aussi
-- des NULL structurels sans rapport (cf. audit complétude), qu'il ne faut
-- pas confondre avec cette correction.
UPDATE diagnostic_dpe_flux f
SET surface_habitable_logement = NULL
FROM diagnostic_dpe d
WHERE f.numero_dpe = d.numero_dpe
  AND d.type_batiment = 'appartement'
  AND f.surface_habitable_logement > 400;

-- ============================================================
-- Décisions documentées de NE PAS corriger (cf. docs/09_tp3_audit_qualite.md
-- pour le détail) :
--
-- - annee_construction < 1700 (34 lignes) : conservées telles quelles. Le
--   bâti ancien existe réellement en Loire-Atlantique (centres historiques,
--   côtière) ; rien ne prouve que ces valeurs soient fausses, les supprimer
--   ou les corriger serait une décision non justifiable sur la seule base
--   de leur rareté statistique.
--
-- - surface_reelle_bati / type_local / nombre_pieces_principales /
--   surface_terrain NULL sur transaction_dvf (mutations sans bâti :
--   terrain nu, dépendance) : absence structurelle et légitime, pas une
--   anomalie. Imputer une surface bâtie sur une vente de terrain nu serait
--   une erreur, pas une correction.
--
-- - 22 mutations à prix/m² > 15 000 €/m² (après agrégation correcte par
--   id_mutation) : chaque valeur individuelle (valeur_fonciere,
--   surface_reelle_bati) est probablement exacte en tant que telle ; le
--   ratio prix/m² n'est simplement pas interprétable à ce niveau de
--   granularité pour ces mutations (ventes en bloc multi-lots avec
--   surface partiellement renseignée, ou marché de niche haut de gamme
--   réel sur le littoral). Aucune ligne modifiée ; à exclure explicitement
--   de tout calcul de prix moyen au m² qui les inclurait.
--
-- - annee_construction NULL sur 34 % de diagnostic_dpe : aucune imputation
--   (fabriquer une année précise sur un tel volume introduirait plus de
--   biais que ça n'en résout). periode_construction, complet à 100 %,
--   reste disponible comme substitut pour toute analyse par époque de
--   construction.
-- ============================================================
