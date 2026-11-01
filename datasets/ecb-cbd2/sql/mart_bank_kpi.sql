-- mart_bank_kpi: KPI bancari per paese/trimestre
--
-- Una colonna = una serie dichiarata in series_catalog.csv. Nessun AVG tra
-- serie: ogni MAX(CASE ...) seleziona una sola serie, gia' normalizzata in
-- punti percentuali dal clean.
-- Aggregati BCE esclusi dal campo `paese`: B0 = area euro, U2 = Unione europea.

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        MAX(CASE WHEN metrica = 'roe' THEN valore END) AS roe_pct,
        MAX(CASE WHEN metrica = 'roa' THEN valore END) AS roa_pct,
        MAX(CASE WHEN metrica = 'costo_reddito' THEN valore END) AS costo_reddito_pct,
        MAX(CASE WHEN metrica = 'margine_interesse' THEN valore END) AS margine_interesse_pct,
        MAX(CASE WHEN metrica = 'cet1' THEN valore END) AS cet1_pct,
        MAX(CASE WHEN metrica = 'tier1' THEN valore END) AS tier1_pct,
        MAX(CASE WHEN metrica = 'solvency' THEN valore END) AS solvency_ratio_pct,
        MAX(CASE WHEN metrica = 'npl' THEN valore END) AS npl_ratio_pct,
        MAX(CASE WHEN metrica = 'npl_famiglie' THEN valore END) AS npl_ratio_famiglie_pct,
        MAX(CASE WHEN metrica = 'npl_imprese' THEN valore END) AS npl_ratio_imprese_pct,
        MAX(CASE WHEN metrica = 'copertura_npl' THEN valore END) AS copertura_npl_pct,
        MAX(CASE WHEN metrica = 'lcr' THEN valore END) AS lcr_pct,
        MAX(CASE WHEN metrica = 'prestiti_depositi' THEN valore END) AS prestiti_deposits_pct,
        MAX(CASE WHEN metrica = 'prestiti_attivo' THEN valore END) AS prestiti_attivo_pct,
        MAX(CASE WHEN metrica = 'prestiti_attivo_nonfin' THEN valore END) AS prestiti_attivo_nonfin_pct
    FROM clean_input
    WHERE trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F', 'B0')
    GROUP BY paese, anno, trimestre
)

SELECT
    paese,
    anno,
    trimestre,
    ROUND(roe_pct, 2) AS roe_pct,
    ROUND(roa_pct, 2) AS roa_pct,
    ROUND(costo_reddito_pct, 2) AS costo_reddito_pct,
    ROUND(margine_interesse_pct, 2) AS margine_interesse_pct,
    ROUND(cet1_pct, 2) AS cet1_pct,
    ROUND(tier1_pct, 2) AS tier1_pct,
    ROUND(solvency_ratio_pct, 2) AS solvency_ratio_pct,
    ROUND(npl_ratio_pct, 2) AS npl_ratio_pct,
    ROUND(npl_ratio_famiglie_pct, 2) AS npl_ratio_famiglie_pct,
    ROUND(npl_ratio_imprese_pct, 2) AS npl_ratio_imprese_pct,
    ROUND(copertura_npl_pct, 2) AS copertura_npl_pct,
    ROUND(lcr_pct, 2) AS lcr_pct,
    ROUND(prestiti_deposits_pct, 2) AS prestiti_deposits_pct,
    ROUND(prestiti_attivo_pct, 2) AS prestiti_attivo_pct,
    ROUND(prestiti_attivo_nonfin_pct, 2) AS prestiti_attivo_nonfin_pct
FROM serie
ORDER BY paese, anno, trimestre
