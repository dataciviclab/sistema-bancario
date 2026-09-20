-- clean.sql: ECB BSI Balance Sheet Items
-- Fedele al raw: solo rinomina colonne, normalizza tipi, estrae year/quarter

WITH raw AS (
    SELECT * FROM raw_input
    -- Filtro solo item che servono (il resto e rumoroso)
    WHERE BS_ITEM IN ('T00', 'A20T', 'L20', 'L21', 'L22', 'L23', 'L40', 'L60')
)

SELECT
    -- Dimensioni
    REF_AREA AS paese,
    BS_ITEM AS voce,
    TIME_PERIOD AS periodo,
    -- Metrica
    CAST(OBS_VALUE AS DOUBLE) AS valore,
    -- Metadati
    FREQ AS frequenza,
    BS_REP_SECTOR AS settore,
    MATURITY_ORIG AS scadenza,
    UNIT AS unita,
    -- Year/quarter
    CASE
        WHEN TIME_PERIOD LIKE '%-Q%' THEN CAST(SPLIT_PART(TIME_PERIOD, '-Q', 1) AS INTEGER)
        WHEN TIME_PERIOD LIKE '%-%' THEN CAST(SPLIT_PART(TIME_PERIOD, '-', 1) AS INTEGER)
        ELSE CAST(TIME_PERIOD AS INTEGER)
    END AS anno,
    CASE
        WHEN TIME_PERIOD LIKE '%-Q1' THEN 'T1'
        WHEN TIME_PERIOD LIKE '%-Q2' THEN 'T2'
        WHEN TIME_PERIOD LIKE '%-Q3' THEN 'T3'
        WHEN TIME_PERIOD LIKE '%-Q4' THEN 'T4'
        WHEN TIME_PERIOD LIKE '%-01' THEN 'T1'
        WHEN TIME_PERIOD LIKE '%-02' THEN 'T1'
        WHEN TIME_PERIOD LIKE '%-03' THEN 'T1'
        WHEN TIME_PERIOD LIKE '%-04' THEN 'T2'
        WHEN TIME_PERIOD LIKE '%-05' THEN 'T2'
        WHEN TIME_PERIOD LIKE '%-06' THEN 'T2'
        WHEN TIME_PERIOD LIKE '%-07' THEN 'T3'
        WHEN TIME_PERIOD LIKE '%-08' THEN 'T3'
        WHEN TIME_PERIOD LIKE '%-09' THEN 'T3'
        WHEN TIME_PERIOD LIKE '%-10' THEN 'T4'
        WHEN TIME_PERIOD LIKE '%-11' THEN 'T4'
        WHEN TIME_PERIOD LIKE '%-12' THEN 'T4'
        ELSE NULL
    END AS trimestre
FROM raw
WHERE CAST(OBS_VALUE AS DOUBLE) IS NOT NULL
ORDER BY paese, voce, periodo
