-- clean.sql: ECB MIR — MFI Interest Rates
--
-- Contratto: solo le serie dichiarate in series_catalog.csv entrano nel clean.
-- Il clean precedente teneva `voce` + `scadenza` e buttava via classe di
-- importo, settore controparte e copertura: i mart finivano per mediare fino a
-- 24 serie diverse dietro un solo "tasso sui mutui".
--
-- Frequenza: la BCE pubblica MIR solo a frequenza mensile. Il trimestre e'
-- derivato dal mese; l'aggregazione trimestrale (media di 3 mesi della STESSA
-- serie) vive nel mart, non qui.

WITH catalogo AS (
    SELECT
        metrica,
        serie_id,
        descrizione,
        unita,
        CAST(moltiplicatore AS DOUBLE) AS moltiplicatore
    FROM read_csv('datasets/ecb-mir/series_catalog.csv', header = true, auto_detect = true)
),

raw AS (
    SELECT * FROM raw_input
),

normalizzato AS (
    SELECT
        REF_AREA AS paese,
        BS_ITEM AS voce,
        FREQ AS frequenza,
        TIME_PERIOD AS periodo,
        CAST(OBS_VALUE AS DOUBLE) AS valore_grezzo,
        KEY AS chiave,
        CONCAT_WS(
            '|',
            COALESCE(BS_ITEM, ''),
            COALESCE(BS_REP_SECTOR, ''),
            COALESCE(MATURITY_NOT_IRATE, ''),
            COALESCE(DATA_TYPE_MIR, ''),
            COALESCE(AMOUNT_CAT, ''),
            COALESCE(BS_COUNT_SECTOR, ''),
            COALESCE(CURRENCY_TRANS, ''),
            COALESCE(IR_BUS_COV, '')
        ) AS serie_id,
        CASE
            WHEN TIME_PERIOD LIKE '%-Q%' THEN CAST(SPLIT_PART(TIME_PERIOD, '-Q', 1) AS INTEGER)
            ELSE CAST(SPLIT_PART(TIME_PERIOD, '-', 1) AS INTEGER)
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
ORDER BY metrica, paese, anno, trimestre, periodo
