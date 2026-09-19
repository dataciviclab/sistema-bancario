-- clean.sql: ECB BLS Bank Lending Survey
-- Fedele al raw: solo rinomina colonne, normalizza tipi, estrae year/quarter

SELECT
    -- Dimensioni
    REF_AREA AS paese,
    BLS_ITEM AS voce,
    TIME_PERIOD AS periodo,
    -- Metrica
    CAST(OBS_VALUE AS DOUBLE) AS valore,
    -- Metadati
    BLS_COUNT AS num_banche,
    -- Year/quarter
    CASE
        WHEN TIME_PERIOD LIKE '%-Q%' THEN CAST(SPLIT_PART(TIME_PERIOD, '-Q', 1) AS INTEGER)
        ELSE NULL
    END AS anno,
    CASE
        WHEN TIME_PERIOD LIKE '%-Q1' THEN 'T1'
        WHEN TIME_PERIOD LIKE '%-Q2' THEN 'T2'
        WHEN TIME_PERIOD LIKE '%-Q3' THEN 'T3'
        WHEN TIME_PERIOD LIKE '%-Q4' THEN 'T4'
        ELSE NULL
    END AS trimestre
FROM raw_input
WHERE CAST(OBS_VALUE AS DOUBLE) IS NOT NULL
ORDER BY paese, voce, periodo
