-- Vérification que les relations fonctionnent après import

-- Comptages par table
SELECT 'commune' AS table_name, COUNT(*) FROM commune
UNION ALL
SELECT 'transaction_dvf', COUNT(*) FROM transaction_dvf
UNION ALL
SELECT 'diagnostic_dpe', COUNT(*) FROM diagnostic_dpe;

-- Aucune transaction ne doit référencer une commune inexistante (garanti par la FK, contrôle explicite)
SELECT COUNT(*) AS transactions_orphelines
FROM transaction_dvf t
LEFT JOIN commune c ON c.code_insee = t.code_insee
WHERE c.code_insee IS NULL;

-- Aucun diagnostic ne doit référencer une commune inexistante
SELECT COUNT(*) AS diagnostics_orphelins
FROM diagnostic_dpe d
LEFT JOIN commune c ON c.code_insee = d.code_insee
WHERE c.code_insee IS NULL;

-- Jointure de bout en bout : nombre de transactions et de diagnostics par commune
-- Remarque : jointure directe transaction + diagnostic sur commune = produit cartésien
-- (une commune avec 15 000 transactions et 50 000 diagnostics donne 750M lignes avant
-- agrégation, cf. docs/annexe_audit_qualite.md). On agrège chaque table séparément.
SELECT
    c.nom_commune,
    (SELECT COUNT(*) FROM transaction_dvf t WHERE t.code_insee = c.code_insee) AS nb_transactions,
    (SELECT COUNT(*) FROM diagnostic_dpe d WHERE d.code_insee = c.code_insee)  AS nb_diagnostics
FROM commune c
ORDER BY nb_transactions DESC
LIMIT 10;
