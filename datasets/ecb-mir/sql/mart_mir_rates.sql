-- mart_mir_rates: tassi bancari per paese/trimestre
--
-- Una colonna = una serie dichiarata. L'unico AVG ammesso e' quello sui mesi
-- della stessa serie (MIR e' mensile, il mart e' trimestrale): media di 3
-- osservazioni della medesima serie, non di serie diverse.

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        AVG(CASE WHEN metrica = 'tasso_mutuo' THEN valore END) AS tasso_mutuo_pct,
        AVG(CASE WHEN metrica = 'tasso_mutuo_variabile' THEN valore END) AS tasso_mutuo_variabile_pct,
        AVG(CASE WHEN metrica = 'tasso_mutuo_fisso_1_5a' THEN valore END) AS tasso_mutuo_fisso_1_5a_pct,
        AVG(CASE WHEN metrica = 'tasso_mutuo_fisso_5_10a' THEN valore END) AS tasso_mutuo_fisso_5_10a_pct,
        AVG(CASE WHEN metrica = 'tasso_imprese' THEN valore END) AS tasso_imprese_pct,
        AVG(CASE WHEN metrica = 'tasso_imprese_piccole' THEN valore END) AS tasso_imprese_piccole_pct,
        AVG(CASE WHEN metrica = 'tasso_consumo' THEN valore END) AS tasso_consumo_pct,
        AVG(CASE WHEN metrica = 'tasso_depositi_overnight' THEN valore END) AS tasso_depositi_overnight_pct,
        AVG(CASE WHEN metrica = 'tasso_depositi_scadenza' THEN valore END) AS tasso_depositi_scadenza_pct,
        AVG(CASE WHEN metrica = 'tasso_depositi_preavviso' THEN valore END) AS tasso_depositi_preavviso_pct,
        COUNT(DISTINCT periodo) AS mesi_osservati
    FROM clean_input
    WHERE trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F')
    GROUP BY paese, anno, trimestre
)

SELECT
    paese,
    anno,
    trimestre,
    ROUND(tasso_mutuo_pct, 2) AS tasso_mutuo_pct,
    ROUND(tasso_mutuo_variabile_pct, 2) AS tasso_mutuo_variabile_pct,
    ROUND(tasso_mutuo_fisso_1_5a_pct, 2) AS tasso_mutuo_fisso_1_5a_pct,
    ROUND(tasso_mutuo_fisso_5_10a_pct, 2) AS tasso_mutuo_fisso_5_10a_pct,
    ROUND(tasso_imprese_pct, 2) AS tasso_imprese_pct,
    ROUND(tasso_imprese_piccole_pct, 2) AS tasso_imprese_piccole_pct,
    ROUND(tasso_consumo_pct, 2) AS tasso_consumo_pct,
    ROUND(tasso_depositi_overnight_pct, 2) AS tasso_depositi_overnight_pct,
    ROUND(tasso_depositi_scadenza_pct, 2) AS tasso_depositi_scadenza_pct,
    ROUND(tasso_depositi_preavviso_pct, 2) AS tasso_depositi_preavviso_pct,
    ROUND(tasso_mutuo_pct - tasso_depositi_scadenza_pct, 2) AS spread_mutuo_deposito_pp,
    ROUND(tasso_imprese_pct - tasso_depositi_overnight_pct, 2) AS spread_imprese_overnight_pp,
    mesi_osservati
FROM serie
-- Paesi senza la serie "mutui alle famiglie" (CY, EE, GR, LU, LV, MT, SI al
-- 2024): senza il tasso guida la riga non e' leggibile, quindi non entra.
WHERE tasso_mutuo_pct IS NOT NULL
ORDER BY paese, anno, trimestre
