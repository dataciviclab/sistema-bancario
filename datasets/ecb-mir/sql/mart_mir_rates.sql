-- mart_mir_rates: Tassi di interesse per paese/trimestre
-- Filtra: solo tassi (R), solo new business (N), solo voci principali
-- Aggrega a livello trimestrale (media dei 3 mesi)

SELECT
    paese,
    anno,
    trimestre,
    -- Tassi (media trimestrale)
    ROUND(AVG(CASE WHEN voce = 'A2C' AND scadenza = 'A' THEN valore END), 2) AS tasso_mutuo_pct,
    ROUND(AVG(CASE WHEN voce = 'A2C' AND scadenza = 'F' THEN valore END), 2) AS tasso_mutuo_variabile_pct,
    ROUND(AVG(CASE WHEN voce = 'A2C' AND scadenza = 'I' THEN valore END), 2) AS tasso_mutuo_fisso_1_5a_pct,
    ROUND(AVG(CASE WHEN voce = 'A2A' AND scadenza = 'A' THEN valore END), 2) AS tasso_imprese_pct,
    ROUND(AVG(CASE WHEN voce = 'A2B' AND scadenza = 'A' THEN valore END), 2) AS tasso_consumo_pct,
    ROUND(AVG(CASE WHEN voce = 'L21' THEN valore END), 2) AS tasso_depositi_overnight_pct,
    ROUND(AVG(CASE WHEN voce = 'L22' THEN valore END), 2) AS tasso_depositi_scadenza_pct,
    ROUND(AVG(CASE WHEN voce = 'L23' THEN valore END), 2) AS tasso_depositi_preavviso_pct,
    -- Spread
    ROUND(
        AVG(CASE WHEN voce = 'A2C' AND scadenza = 'A' THEN valore END) -
        AVG(CASE WHEN voce = 'L22' THEN valore END)
    , 2) AS spread_mutuo_deposito_pp,
    ROUND(
        AVG(CASE WHEN voce = 'A2A' AND scadenza = 'A' THEN valore END) -
        AVG(CASE WHEN voce = 'L21' THEN valore END)
    , 2) AS spread_imprese_overnight_pp
FROM clean_input
WHERE tipo_dato = 'R'
  AND copertura_attivita = 'N'
  AND voce IN ('A2C', 'A2A', 'A2B', 'L21', 'L22', 'L23')
  AND trimestre IS NOT NULL
GROUP BY paese, anno, trimestre
ORDER BY paese, anno, trimestre
