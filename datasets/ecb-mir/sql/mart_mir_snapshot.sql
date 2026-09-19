-- mart_mir_snapshot: Ultimo trimestre per paese
-- Pivot da clean_input (dati unpivoted)

WITH pivoted AS (
    SELECT
        paese, anno, trimestre, periodo,
        MAX(CASE WHEN voce = 'A2C' AND scadenza = 'A' THEN valore END) AS tasso_mutuo_pct,
        MAX(CASE WHEN voce = 'A2C' AND scadenza = 'F' THEN valore END) AS tasso_mutuo_variabile_pct,
        MAX(CASE WHEN voce = 'A2C' AND scadenza = 'I' THEN valore END) AS tasso_mutuo_fisso_1_5a_pct,
        MAX(CASE WHEN voce = 'A2A' AND scadenza = 'A' THEN valore END) AS tasso_imprese_pct,
        MAX(CASE WHEN voce = 'A2B' AND scadenza = 'A' THEN valore END) AS tasso_consumo_pct,
        MAX(CASE WHEN voce = 'L21' THEN valore END) AS tasso_depositi_overnight_pct,
        MAX(CASE WHEN voce = 'L22' THEN valore END) AS tasso_depositi_scadenza_pct,
        MAX(CASE WHEN voce = 'L23' THEN valore END) AS tasso_depositi_preavviso_pct,
        ROW_NUMBER() OVER (PARTITION BY paese ORDER BY anno DESC, trimestre DESC) AS rn
    FROM clean_input
    WHERE tipo_dato = 'R'
      AND copertura_attivita = 'N'
      AND voce IN ('A2C', 'A2A', 'A2B', 'L21', 'L22', 'L23')
      AND trimestre IS NOT NULL
    GROUP BY paese, anno, trimestre, periodo
)
SELECT
    paese, anno, trimestre, periodo,
    tasso_mutuo_pct, tasso_mutuo_variabile_pct, tasso_mutuo_fisso_1_5a_pct,
    tasso_imprese_pct, tasso_consumo_pct,
    tasso_depositi_overnight_pct, tasso_depositi_scadenza_pct, tasso_depositi_preavviso_pct,
    ROUND(tasso_mutuo_pct - tasso_depositi_scadenza_pct, 2) AS spread_mutuo_deposito_pp,
    ROUND(tasso_imprese_pct - tasso_depositi_overnight_pct, 2) AS spread_imprese_overnight_pp
FROM pivoted
WHERE rn = 1
ORDER BY paese
