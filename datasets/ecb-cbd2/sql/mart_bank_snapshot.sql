-- mart_bank_snapshot: Ultimo trimestre per paese

WITH pivoted AS (
    SELECT
        paese, anno, trimestre,
        ROUND(AVG(CASE WHEN indicatore = 'I2003' THEN valore END), 2) AS roe_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I2004' THEN valore END), 2) AS roa_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I2100' THEN valore END), 2) AS costo_reddito_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I2120' THEN valore END), 2) AS margine_interesse_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I4008' THEN valore END), 2) AS cet1_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I4002' THEN valore END), 2) AS tier1_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I4007' THEN valore END), 2) AS capitale_totale_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I3632' THEN valore END), 2) AS npl_ratio_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I3631' THEN valore END), 2) AS copertura_npl_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I3017' THEN valore END), 2) AS lcr_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I3006' THEN valore END), 2) AS prestiti_deposits_pct,
        ROUND(AVG(CASE WHEN indicatore = 'I3160' THEN valore END), 2) AS prestiti_attivo_pct,
        ROW_NUMBER() OVER (PARTITION BY paese ORDER BY anno DESC, trimestre DESC) AS rn
    FROM clean_input
    WHERE trimestre IS NOT NULL
    GROUP BY paese, anno, trimestre
)
SELECT
    paese, anno, trimestre,
    roe_pct, roa_pct, costo_reddito_pct, margine_interesse_pct,
    cet1_pct, tier1_pct, capitale_totale_pct,
    npl_ratio_pct, copertura_npl_pct,
    lcr_pct, prestiti_deposits_pct, prestiti_attivo_pct
FROM pivoted
WHERE rn = 1
ORDER BY paese
