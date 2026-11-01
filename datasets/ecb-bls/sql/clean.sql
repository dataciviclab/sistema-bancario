-- clean.sql: ECB BLS — Bank Lending Survey
--
-- Contratto: solo le serie dichiarate in series_catalog.csv.
--
-- La versione precedente mappava `BLS_ITEM` su nomi inventati: 'BC' diventava
-- "condizioni di credito alle imprese" ma in realta' e' "impatto della
-- concorrenza bancaria"; 'SME' e 'LE' sono classi dimensionali, non item; 'LP'
-- e' "impatto della posizione di liquidita'". Risultato: etichette sbagliate su
-- numeri presi a caso. Qui ogni metrica e' una combinazione esplicita di
-- item, tipo cliente, dettaglio, orizzonte, dominio e ruolo.

WITH catalogo AS (
    SELECT
        metrica,
        serie_id,
        descrizione,
        unita,
        CAST(moltiplicatore AS DOUBLE) AS moltiplicatore
    FROM read_csv('datasets/ecb-bls/series_catalog.csv', header = true, auto_detect = true)
),

raw AS (
    SELECT * FROM raw_input
),

normalizzato AS (
    SELECT
        REF_AREA AS paese,
        BLS_ITEM AS voce,
        FREQ AS frequenza,
        TIME_PERIOD AS periodo,
        CAST(OBS_VALUE AS DOUBLE) AS valore_grezzo,
        KEY AS chiave,
        CONCAT_WS(
            '|',
            COALESCE(BLS_ITEM, ''),
            COALESCE(BLS_COUNT, ''),
            COALESCE(BLS_COUNT_DETAIL, ''),
            COALESCE(TIME_HORIZON, ''),
            COALESCE(EFFECT_DOMAIN, ''),
            COALESCE(MARKET_ROLE, ''),
            COALESCE(BLS_AGG_METHOD, '')
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
