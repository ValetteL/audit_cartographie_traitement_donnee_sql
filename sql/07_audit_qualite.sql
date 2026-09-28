-- TP3 — Audit qualité & nettoyage des données
-- Requêtes d'audit, organisées selon les 5 dimensions de la matrice de contrôles
-- (docs/09_tp3_audit_qualite.md). Ce script est exécuté deux fois à l'identique :
-- une fois AVANT sql/08_nettoyage.sql (état initial), une fois APRÈS (recontrôle),
-- pour produire le comparatif avant/après documenté dans le rapport.
--
-- Périmètre : les 3 tables statiques du TP1 (commune, transaction_dvf,
-- diagnostic_dpe) et la table temps réel du TP2 (diagnostic_dpe_flux), qui
-- dépend référentiellement des deux premières.

-- ============================================================
-- 1. COMPLÉTUDE — valeurs manquantes sur les champs significatifs
-- ============================================================

-- Champs clés, toutes tables confondues. Certains NULL sont attendus et
-- documentés comme tels (ex. surface_reelle_bati NULL pour une mutation sans
-- bâti) : ce contrôle mesure le volume, l'interprétation est faite au cas par
-- cas dans le rapport, pas ici.
SELECT 'diagnostic_dpe' AS table_name, 'annee_construction' AS colonne,
       COUNT(*) FILTER (WHERE annee_construction IS NULL) AS n_null, COUNT(*) AS total
FROM diagnostic_dpe
UNION ALL SELECT 'diagnostic_dpe', 'surface_habitable_logement',
       COUNT(*) FILTER (WHERE surface_habitable_logement IS NULL), COUNT(*) FROM diagnostic_dpe
UNION ALL SELECT 'diagnostic_dpe', 'adresse',
       COUNT(*) FILTER (WHERE adresse IS NULL), COUNT(*) FROM diagnostic_dpe
UNION ALL SELECT 'diagnostic_dpe_flux', 'surface_habitable_logement',
       COUNT(*) FILTER (WHERE surface_habitable_logement IS NULL), COUNT(*) FROM diagnostic_dpe_flux
UNION ALL SELECT 'transaction_dvf', 'surface_reelle_bati',
       COUNT(*) FILTER (WHERE surface_reelle_bati IS NULL), COUNT(*) FROM transaction_dvf
UNION ALL SELECT 'transaction_dvf', 'type_local',
       COUNT(*) FILTER (WHERE type_local IS NULL), COUNT(*) FROM transaction_dvf
UNION ALL SELECT 'transaction_dvf', 'longitude',
       COUNT(*) FILTER (WHERE longitude IS NULL), COUNT(*) FROM transaction_dvf
ORDER BY 1, 2;

-- Vérification que le NULL de surface_reelle_bati est bien structurel (lié à
-- la nature du bien) et non aléatoire : 0 attendu pour Maison/Appartement.
SELECT type_local, COUNT(*) FILTER (WHERE surface_reelle_bati IS NULL) AS n_null
FROM transaction_dvf
WHERE type_local IN ('Maison', 'Appartement')
GROUP BY type_local;

-- ============================================================
-- 2. UNICITÉ
-- ============================================================

-- numero_dpe (PK) et id_transaction (PK) garantissent déjà l'absence de
-- doublon strict. Contrôle du risque de faux positif à l'intuition naïve
-- "même adresse + même date = doublon" : à vérifier avant de l'utiliser
-- comme règle, car les immeubles collectifs regroupent plusieurs logements
-- (donc plusieurs DPE légitimement distincts) sous une même adresse/date de
-- campagne de diagnostic.
SELECT adresse, date_etablissement_dpe, COUNT(*) AS n
FROM diagnostic_dpe
WHERE adresse IS NOT NULL
GROUP BY adresse, date_etablissement_dpe
HAVING COUNT(*) > 1
ORDER BY n DESC
LIMIT 10;

-- Cohérence interne des mutations multi-lots : une même valeur_fonciere
-- doit être strictement identique sur toutes les lignes d'un même
-- id_mutation (c'est la donnée source qui la répète, elle ne doit jamais
-- diverger au sein d'une mutation).
SELECT id_mutation, COUNT(*) AS n_lignes, COUNT(DISTINCT valeur_fonciere) AS n_valeurs_distinctes
FROM transaction_dvf
GROUP BY id_mutation
HAVING COUNT(*) > 1 AND COUNT(DISTINCT valeur_fonciere) > 1;

-- ============================================================
-- 3. VALIDITÉ — valeurs hors bornes plausibles
-- ============================================================

-- nombre_pieces_principales = 0 est attendu pour les biens sans pièces
-- d'habitation (Dépendance, local commercial) ; c'est invalide pour un
-- logement réellement habitable (Maison, Appartement).
SELECT COUNT(*) AS n_pieces_zero_logement
FROM transaction_dvf
WHERE nombre_pieces_principales = 0 AND type_local IN ('Maison', 'Appartement');

-- surface_habitable_logement > 400 m² pour un type "appartement" : borne
-- justifiée par les surfaces d'appartements individuels les plus élevées
-- du marché français (grands duplex/penthouses haut de gamme, rarement
-- au-delà de 300-400 m²) — au-delà, forte suspicion que la surface saisie
-- soit en réalité celle de l'immeuble entier plutôt que du seul logement.
-- Ne s'applique pas aux types "immeuble", où une grande surface est normale.
SELECT numero_dpe, surface_habitable_logement, type_batiment
FROM diagnostic_dpe
WHERE surface_habitable_logement > 400 AND type_batiment = 'appartement'
ORDER BY surface_habitable_logement DESC;

-- annee_construction < 1700 : borne large, volontairement non corrective —
-- objectif ici est de lister les cas, pas de présumer qu'ils sont faux (le
-- bâti ancien existe réellement en Loire-Atlantique). Décision documentée
-- dans le rapport : ces lignes sont conservées telles quelles.
SELECT numero_dpe, annee_construction
FROM diagnostic_dpe
WHERE annee_construction < 1700
ORDER BY annee_construction;

-- ============================================================
-- 4. COHÉRENCE
-- ============================================================

-- Prix au m² par mutation (agrégée, cf. méthodologie de sql/05_requetes_analyse.sql
-- : diviser valeur_fonciere par la surface d'une seule ligne d'une mutation
-- multi-lots produit des prix au m² absurdes — l'agrégation par id_mutation
-- est indispensable avant tout contrôle de cohérence sur le prix).
-- Borne de 15 000 €/m² : environ 1,7 fois le 99e percentile observé sur
-- l'ensemble du jeu de données (~8 800 €/m², cf. docs/09_tp3_audit_qualite.md)
-- — large marge pour ne pas flaguer le marché haut de gamme légitime
-- (littoral, centre de Nantes), tout en isolant les cas manifestement
-- disproportionnés.
WITH mutation AS (
    SELECT id_mutation, MAX(valeur_fonciere) AS valeur_fonciere,
           SUM(surface_reelle_bati) AS surface_totale, MAX(code_insee) AS code_insee
    FROM transaction_dvf
    WHERE surface_reelle_bati IS NOT NULL AND surface_reelle_bati > 0
    GROUP BY id_mutation
)
SELECT m.id_mutation, c.nom_commune, m.valeur_fonciere, m.surface_totale,
       ROUND(m.valeur_fonciere / m.surface_totale) AS prix_m2
FROM mutation m
JOIN commune c ON c.code_insee = m.code_insee
WHERE m.valeur_fonciere / m.surface_totale > 15000
ORDER BY prix_m2 DESC;

-- ============================================================
-- 5. INTÉGRITÉ RÉFÉRENTIELLE
-- ============================================================

-- Déjà garantie par les contraintes FK (rejet à l'insertion) : ce contrôle
-- démontre l'absence d'orphelin plutôt que d'en corriger, résultat attendu = 0
-- partout.
SELECT 'transaction_dvf -> commune' AS relation, COUNT(*) AS n_orphelins
FROM transaction_dvf t LEFT JOIN commune c ON c.code_insee = t.code_insee
WHERE c.code_insee IS NULL
UNION ALL
SELECT 'diagnostic_dpe -> commune', COUNT(*)
FROM diagnostic_dpe d LEFT JOIN commune c ON c.code_insee = d.code_insee
WHERE c.code_insee IS NULL
UNION ALL
SELECT 'diagnostic_dpe_flux -> commune', COUNT(*)
FROM diagnostic_dpe_flux f LEFT JOIN commune c ON c.code_insee = f.code_insee
WHERE c.code_insee IS NULL;
