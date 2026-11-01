-- clean.sql: ECB CBD2 — Consolidated Banking Data
--
-- Contratto: solo le serie dichiarate in series_catalog.csv.
--
-- Il clean precedente teneva `CB_ITEM` e buttava via settore controparte,
-- framework e portfolio: il mart poi faceva AVG su 2-6 serie diverse per cella
-- (es. ROE = media tra "tutte le banche" e "gruppi domestici") e produceva
-- due colonne perennemente NULL (I2120 e I4007 non esistono in CBD2).
--
-- Qui ogni metrica e' una serie esplicita. Gli aggregati BCE (B0 = area euro,
-- U2 = UE) restano nel dato ma vengono esclusi dai mart.

WITH catalogo AS (
    SELECT
        metrica,
        serie_id,
        descrizione,
        unita,
        CAST(moltiplicatore AS DOUBLE) AS moltiplicatore
    FROM read_csv('datasets/ecb-cbd2/series_catalog.csv', header = true, auto_detect = true)
),

raw AS (
    SELECT * FROM raw_input
),

normalizzato AS (
    SELECT
        REF_AREA AS paese,
        CB_ITEM AS voce,
        FREQ AS frequenza,
        TIME_PERIOD AS periodo,
        CAST(OBS_VALUE AS DOUBLE) AS valore_grezzo,
        UNIT_MEASURE AS unita_misura,
        KEY AS chiave,
        CONCAT_WS(
            '|',
            COALESCE(CB_ITEM, ''),
            COALESCE(CB_REP_SECTOR, ''),
            COALESCE(COUNT_AREA, ''),
            COALESCE(BS_COUNT_SECTOR, ''),
            COALESCE(BS_NFC_ACTIVITY, ''),
            COALESCE(CB_SECTOR_SIZE, ''),
            COALESCE(CB_REP_FRAMEWRK, ''),
            COALESCE(CB_PORTFOLIO, ''),
            COALESCE(CB_EXP_TYPE, ''),
            COALESCE(CB_VAL_METHOD, ''),
            COALESCE(MATURITY_RES, ''),
            COALESCE(DATA_TYPE, ''),
            COALESCE(CURRENCY_TRANS, ''),
            COALESCE(UNIT_MEASURE, '')
        ) AS serie_id,
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
            WHEN TIME_PERIOD LIKE '%-01' OR TIME_PERIOD LIKE '%-02' OR TIME_PERIOD LIKE '%-03' THEN 'T1'
            WHEN TIME_PERIOD LIKE '%-04' OR TIME_PERIOD LIKE '%-05' OR TIME_PERIOD LIKE '%-06' THEN 'T2'
            WHEN TIME_PERIOD LIKE '%-07' OR TIME_PERIOD LIKE '%-08' OR TIME_PERIOD LIKE '%-09' THEN 'T3'
            WHEN TIME_PERIOD LIKE '%-10' OR TIME_PERIOD LIKE '%-11' OR TIME_PERIOD LIKE '%-12' THEN 'T4'
            ELSE NULL
        END AS trimestre
    FROM raw
    WHERE CAST(OBS_VALUE AS DOUBLE) IS NOT NULL
),

dichiarate AS (
    SELECT
        n.paese,
        n.anno,
        n.trimestre,
        n.periodo,
        c.metrica,
        c.descrizione,
        c.unita,
        n.serie_id,
        n.chiave,
        n.frequenza,
        ROUND(n.valore_grezzo * c.moltiplicatore, 4) AS valore
    FROM normalizzato n
    JOIN catalogo c ON n.serie_id = c.serie_id
    WHERE n.trimestre IS NOT NULL
)

SELECT
    paese,
    anno,
    trimestre,
    periodo,
    metrica,
    descrizione,
    unita,
    valore,
    serie_id,
    chiave,
    frequenza
FROM dichiarate
ORDER BY metrica, paese, anno, trimestre
