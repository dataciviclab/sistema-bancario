-- mart_bank_kpi: KPI bancari per paese/trimestre
-- Aggrega a livello trimestrale

SELECT
    paese,
    anno,
    trimestre,
    -- Profittabilita
    ROUND(AVG(CASE WHEN indicatore = 'I2003' THEN valore END), 2) AS roe_pct,
    ROUND(AVG(CASE WHEN indicatore = 'I2004' THEN valore END), 2) AS roa_pct,
    ROUND(AVG(CASE WHEN indicatore = 'I2100' THEN valore END), 2) AS costo_reddito_pct,
    ROUND(AVG(CASE WHEN indicatore = 'I2120' THEN valore END), 2) AS margine_interesse_pct,
    ROUND(AVG(CASE WHEN indicatore = 'I2410' THEN valore END), 2) AS redditi_interesse_pct,
    -- Capitale
    ROUND(AVG(CASE WHEN indicatore = 'I4008' THEN valore END), 2) AS cet1_pct,
    ROUND(AVG(CASE WHEN indicatore = 'I4002' THEN valore END), 2) AS tier1_pct,
    ROUND(AVG(CASE WHEN indicatore = 'I4007' THEN valore END), 2) AS capitale_totale_pct,
    -- Qualita del credito
    ROUND(AVG(CASE WHEN indicatore = 'I3632' THEN valore END), 2) AS npl_ratio_pct,
    ROUND(AVG(CASE WHEN indicatore = 'I3631' THEN valore END), 2) AS copertura_npl_pct,
    -- Liquidita
    ROUND(AVG(CASE WHEN indicatore = 'I3017' THEN valore END), 2) AS lcr_pct,
    ROUND(AVG(CASE WHEN indicatore = 'I3006' THEN valore END), 2) AS prestiti_deposits_pct,
    -- Bilancio
    ROUND(AVG(CASE WHEN indicatore = 'I3160' THEN valore END), 2) AS prestiti_attivo_pct,
    ROUND(AVG(CASE WHEN indicatore = 'I0001' THEN valore END), 0) AS dim_media_banche
FROM clean_input
WHERE trimestre IS NOT NULL
GROUP BY paese, anno, trimestre
ORDER BY paese, anno, trimestre
