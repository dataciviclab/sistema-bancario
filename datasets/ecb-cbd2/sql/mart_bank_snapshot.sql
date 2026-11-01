-- mart_bank_snapshot: ultimo trimestre disponibile per paese
--
-- Stesse serie dichiarate di mart_bank_kpi, stesso perimetro: un confronto
-- cross-country non deve mostrare numeri diversi dalla serie trimestrale.

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        MAX(CASE WHEN metrica = 'roe' THEN valore END) AS roe_pct,
        MAX(CASE WHEN metrica = 'roa' THEN valore END) AS roa_pct,
        MAX(CASE WHEN metrica = 'costo_reddito' THEN valore END) AS costo_reddito_pct,
        MAX(CASE WHEN metrica = 'cet1' THEN valore END) AS cet1_pct,
        MAX(CASE WHEN metrica = 'npl' THEN valore END) AS npl_ratio_pct,
        MAX(CASE WHEN metrica = 'copertura_npl' THEN valore END) AS copertura_npl_pct,
        MAX(CASE WHEN metrica = 'lcr' THEN valore END) AS lcr_pct,
        MAX(CASE WHEN metrica = 'prestiti_depositi' THEN valore END) AS prestiti_deposits_pct
    FROM clean_input
    WHERE trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F', 'B0')
    GROUP BY paese, anno, trimestre
),

ultimo AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY paese ORDER BY anno DESC, trimestre DESC) AS rn
    FROM serie
    WHERE roe_pct IS NOT NULL
)

SELECT
    paese,
    anno,
    trimestre,
    ROUND(roe_pct, 2) AS roe_pct,
    ROUND(roa_pct, 2) AS roa_pct,
    ROUND(costo_reddito_pct, 2) AS costo_reddito_pct,
    ROUND(cet1_pct, 2) AS cet1_pct,
    ROUND(npl_ratio_pct, 2) AS npl_ratio_pct,
    ROUND(copertura_npl_pct, 2) AS copertura_npl_pct,
    ROUND(lcr_pct, 2) AS lcr_pct,
    ROUND(prestiti_deposits_pct, 2) AS prestiti_deposits_pct
FROM ultimo
WHERE rn = 1
ORDER BY paese
