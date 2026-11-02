-- mart_benchmark: aggregati ufficiali per il confronto
--
-- Perche' un mart separato: gli aggregati (U2 = area euro, B0 = Unione
-- europea, secondo il codelist CL_AREA della BCE) non vanno nei mart per
-- paese, altrimenti chi fa un join o una media li conta come se fossero paesi.
-- Restano qui, con il nome esteso accanto al codice, e il consumatore li
-- chiama per confronto.
--
-- U2 = "Euro area (Member States and Institutions of the Euro Area)"
-- B0 = "EU (Member States and Institutions of the European Union)"

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
    WHERE paese IN ('U2', 'B0')
      AND trimestre IS NOT NULL
    GROUP BY paese, anno, trimestre
)

SELECT
    paese AS area,
    CASE paese
        WHEN 'U2' THEN 'Area euro'
        WHEN 'B0' THEN 'Unione europea'
    END AS area_nome,
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
FROM serie
WHERE roe_pct IS NOT NULL
ORDER BY area, anno, trimestre
