-- Requêtes répondant à la problématique du TP (cf. docs/01_presentation_sujet.md) :
-- existe-t-il un écart de prix entre communes selon la performance énergétique du parc ?
--
-- Note méthodologique (cf. docs/annexe_audit_qualite.md) : dans DVF, une mutation portant
-- sur plusieurs lots (ex. un lotissement de plusieurs maisons vendu en une seule transaction)
-- est répartie sur plusieurs lignes qui répètent toutes la même valeur_fonciere (le prix
-- total de la mutation, pas celui d'un lot). Diviser valeur_fonciere par la surface de
-- chaque ligne individuellement surestime donc massivement le prix au m² de ces mutations.
-- On agrège d'abord par id_mutation (une valeur_fonciere, somme des surfaces des lots
-- Maison/Appartement) avant de calculer un prix au m², pour éviter ce biais.

-- 1. Prix moyen au m² par commune (agrégé par mutation, maisons et appartements, surface > 0)
WITH mutation AS (
    SELECT
        t.id_mutation,
        t.code_insee,
        MAX(t.valeur_fonciere) AS valeur_fonciere,
        SUM(t.surface_reelle_bati) AS surface_totale
    FROM transaction_dvf t
    WHERE t.type_local IN ('Maison', 'Appartement')
      AND t.surface_reelle_bati > 0
      AND t.nature_mutation = 'Vente'
    GROUP BY t.id_mutation, t.code_insee
)
SELECT
    c.nom_commune,
    COUNT(*) AS nb_mutations,
    ROUND(AVG(m.valeur_fonciere / NULLIF(m.surface_totale, 0))::numeric, 0) AS prix_moyen_m2
FROM mutation m
JOIN commune c ON c.code_insee = m.code_insee
GROUP BY c.nom_commune
HAVING COUNT(*) >= 10
ORDER BY prix_moyen_m2 DESC;

-- 2. Répartition des étiquettes DPE par commune (part de logements F/G = "passoires énergétiques")
SELECT
    c.nom_commune,
    COUNT(*) AS nb_diagnostics,
    ROUND(100.0 * COUNT(*) FILTER (WHERE d.etiquette_dpe IN ('F','G')) / COUNT(*), 1) AS pct_f_g
FROM diagnostic_dpe d
JOIN commune c ON c.code_insee = d.code_insee
GROUP BY c.nom_commune
HAVING COUNT(*) >= 10
ORDER BY pct_f_g DESC;

-- 3. Vue combinée : prix moyen au m² vs part de passoires énergétiques, par commune
WITH mutation AS (
    SELECT
        t.id_mutation,
        t.code_insee,
        MAX(t.valeur_fonciere) AS valeur_fonciere,
        SUM(t.surface_reelle_bati) AS surface_totale
    FROM transaction_dvf t
    WHERE t.type_local IN ('Maison', 'Appartement')
      AND t.surface_reelle_bati > 0
      AND t.nature_mutation = 'Vente'
    GROUP BY t.id_mutation, t.code_insee
),
prix AS (
    SELECT
        m.code_insee,
        COUNT(*) AS nb_mutations,
        AVG(m.valeur_fonciere / NULLIF(m.surface_totale, 0)) AS prix_moyen_m2
    FROM mutation m
    GROUP BY m.code_insee
    HAVING COUNT(*) >= 10
),
energie AS (
    SELECT
        d.code_insee,
        COUNT(*) AS nb_diagnostics,
        100.0 * COUNT(*) FILTER (WHERE d.etiquette_dpe IN ('F','G')) / COUNT(*) AS pct_f_g
    FROM diagnostic_dpe d
    GROUP BY d.code_insee
    HAVING COUNT(*) >= 10
)
SELECT
    c.nom_commune,
    p.nb_mutations,
    ROUND(p.prix_moyen_m2::numeric, 0) AS prix_moyen_m2,
    e.nb_diagnostics,
    ROUND(e.pct_f_g::numeric, 1) AS pct_f_g
FROM prix p
JOIN energie e ON e.code_insee = p.code_insee
JOIN commune c ON c.code_insee = p.code_insee
ORDER BY prix_moyen_m2 DESC;
