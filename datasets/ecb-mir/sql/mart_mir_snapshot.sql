-- mart_mir_snapshot: ultimo trimestre disponibile per paese
--
-- Stesse serie dichiarate di mart_mir_rates, stesso perimetro: il confronto
-- cross-country non puo' mostrare numeri diversi dalla serie trimestrale.

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        AVG(CASE WHEN metrica = 'tasso_mutuo' THEN valore END) AS tasso_mutuo_pct,
        AVG(CASE WHEN metrica = 'tasso_mutuo_variabile' THEN valore END) AS tasso_mutuo_variabile_pct,
        AVG(CASE WHEN metrica = 'tasso_mutuo_fisso_1_5a' THEN valore END) AS tasso_mutuo_fisso_1_5a_pct,
        AVG(CASE WHEN metrica = 'tasso_imprese' THEN valore END) AS tasso_imprese_pct,
        AVG(CASE WHEN metrica = 'tasso_imprese_piccole' THEN valore END) AS tasso_imprese_piccole_pct,
        AVG(CASE WHEN metrica = 'tasso_consumo' THEN valore END) AS tasso_consumo_pct,
        AVG(CASE WHEN metrica = 'tasso_depositi_overnight' THEN valore END) AS tasso_depositi_overnight_pct,
        AVG(CASE WHEN metrica = 'tasso_depositi_scadenza' THEN valore END) AS tasso_depositi_scadenza_pct,
        AVG(CASE WHEN metrica = 'tasso_depositi_preavviso' THEN valore END) AS tasso_depositi_preavviso_pct
    FROM clean_input
    WHERE trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F')
    GROUP BY paese, anno, trimestre
),

ultimo AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY paese ORDER BY anno DESC, trimestre DESC) AS rn
    FROM serie
    WHERE tasso_mutuo_pct IS NOT NULL
)

SELECT
    paese,
    anno,
    trimestre,
    ROUND(tasso_mutuo_pct, 2) AS tasso_mutuo_pct,
    ROUND(tasso_mutuo_variabile_pct, 2) AS tasso_mutuo_variabile_pct,
    ROUND(tasso_mutuo_fisso_1_5a_pct, 2) AS tasso_mutuo_fisso_1_5a_pct,
    ROUND(tasso_imprese_pct, 2) AS tasso_imprese_pct,
    ROUND(tasso_imprese_piccole_pct, 2) AS tasso_imprese_piccole_pct,
    ROUND(tasso_consumo_pct, 2) AS tasso_consumo_pct,
    ROUND(tasso_depositi_overnight_pct, 2) AS tasso_depositi_overnight_pct,
    ROUND(tasso_depositi_scadenza_pct, 2) AS tasso_depositi_scadenza_pct,
    ROUND(tasso_depositi_preavviso_pct, 2) AS tasso_depositi_preavviso_pct,
    ROUND(tasso_mutuo_pct - tasso_depositi_scadenza_pct, 2) AS spread_mutuo_deposito_pp,
    ROUND(tasso_imprese_pct - tasso_depositi_overnight_pct, 2) AS spread_imprese_overnight_pp
FROM ultimo
WHERE rn = 1
ORDER BY paese
