-- Requêtes répondant à la problématique du TP (cf. docs/01_presentation_sujet.md) :
-- existe-t-il un écart de prix entre communes selon la performance énergétique du parc ?

-- 1. Prix moyen au m² par commune (maisons et appartements uniquement, surface > 0)
SELECT
    c.nom_commune,
    COUNT(*) AS nb_ventes,
    ROUND(AVG(t.valeur_fonciere / NULLIF(t.surface_reelle_bati, 0))::numeric, 0) AS prix_moyen_m2
FROM transaction_dvf t
JOIN commune c ON c.code_insee = t.code_insee
WHERE t.type_local IN ('Maison', 'Appartement')
  AND t.surface_reelle_bati > 0
  AND t.nature_mutation = 'Vente'
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
WITH prix AS (
    SELECT
        t.code_insee,
        COUNT(*) AS nb_ventes,
        AVG(t.valeur_fonciere / NULLIF(t.surface_reelle_bati, 0)) AS prix_moyen_m2
    FROM transaction_dvf t
    WHERE t.type_local IN ('Maison', 'Appartement')
      AND t.surface_reelle_bati > 0
      AND t.nature_mutation = 'Vente'
    GROUP BY t.code_insee
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
    p.nb_ventes,
    ROUND(p.prix_moyen_m2::numeric, 0) AS prix_moyen_m2,
    e.nb_diagnostics,
    ROUND(e.pct_f_g::numeric, 1) AS pct_f_g
FROM prix p
JOIN energie e ON e.code_insee = p.code_insee
JOIN commune c ON c.code_insee = p.code_insee
ORDER BY prix_moyen_m2 DESC;
