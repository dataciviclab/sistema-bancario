-- mart_bls_snapshot: Ultimo trimestre per paese
-- Pivot da clean_input

WITH pivoted AS (
    SELECT
        paese, anno, trimestre,
        AVG(CASE WHEN voce = 'BC' THEN valore END) AS cs_imprese,
        AVG(CASE WHEN voce = 'SME' THEN valore END) AS cs_pmi,
        AVG(CASE WHEN voce = 'LE' THEN valore END) AS cs_grandi,
        AVG(CASE WHEN voce = 'MAL' THEN valore END) AS margins_prestiti,
        AVG(CASE WHEN voce = 'NIC' THEN valore END) AS spese_non_interesse,
        AVG(CASE WHEN voce = 'LP' THEN valore END) AS domanda_credito_imprese,
        AVG(CASE WHEN voce = 'CP' THEN valore END) AS domanda_credito_famiglie,
        ROW_NUMBER() OVER (PARTITION BY paese ORDER BY anno DESC, trimestre DESC) AS rn
    FROM clean_input
    WHERE trimestre IS NOT NULL
    AND voce IN ('BC', 'SME', 'LE', 'MAL', 'NIC', 'LP', 'CP')
    GROUP BY paese, anno, trimestre
)
SELECT
    paese, anno, trimestre,
    cs_imprese, cs_pmi, cs_grandi,
    margins_prestiti, spese_non_interesse,
    domanda_credito_imprese, domanda_credito_famiglie
FROM pivoted
WHERE rn = 1
ORDER BY paese
