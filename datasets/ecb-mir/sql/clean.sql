-- clean.sql: ECB MIR MFI Interest Rates
-- Fedele al raw: solo rinomina colonne, normalizza tipi, estrae year/quarter

SELECT
    -- Dimensioni
    REF_AREA AS paese,
    BS_ITEM AS voce,
    MATURITY_NOT_IRATE AS scadenza,
    TIME_PERIOD AS periodo,
    -- Metrica
    CAST(OBS_VALUE AS DOUBLE) AS valore,
    -- Metadati (preservati dal raw, utili per il mart)
    DATA_TYPE_MIR AS tipo_dato,
    IR_BUS_COV AS copertura_attivita,
    BS_REP_SECTOR AS settore,
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
FROM raw_input
WHERE CAST(OBS_VALUE AS DOUBLE) IS NOT NULL
ORDER BY paese, voce, scadenza, periodo
