-- clean.sql: ECB BSI — Balance Sheet Items (feed bancario)
--
-- Contratto: ogni riga appartiene a una serie DICHIARATA in series_catalog.csv.
-- Il catalogo e' la single source of truth: mappa le dimensioni SDMX su un nome
-- di metrica e su un moltiplicatore (mln EUR -> mld EUR).
--
-- Perche' cosi': il clean precedente teneva solo `voce` e buttava via settore,
-- area controparte, tipo dato e valuta. I mart facevano AVG su celle con
-- centinaia di serie diverse (stock EUR + variazioni % + flussi), producendo
-- numeri privi di significato. Qui invece nessuna serie entra per sbaglio:
-- se una serie cambia nome lato BCE, sparisce dal clean e i test falliscono.

WITH catalogo AS (
    SELECT
        metrica,
        serie_id,
        descrizione,
        unita,
        CAST(moltiplicatore AS DOUBLE) AS moltiplicatore
    FROM read_csv('datasets/ecb-bsi/series_catalog.csv', header = true, auto_detect = true)
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
        UNIT AS unita_bce,
        KEY AS chiave,
        -- Identita' della serie: stesse dimensioni del catalogo, senza il paese
        -- (il paese resta nella colonna `paese`, la serie e' condivisa tra paesi).
        CONCAT_WS(
            '|',
            COALESCE(BS_ITEM, ''),
            COALESCE(BS_REP_SECTOR, ''),
            COALESCE(COUNT_AREA, ''),
            COALESCE(BS_COUNT_SECTOR, ''),
            COALESCE(MATURITY_ORIG, ''),
            COALESCE(DATA_TYPE, ''),
            COALESCE(CURRENCY_TRANS, ''),
            COALESCE(ADJUSTMENT, ''),
            COALESCE(BS_SUFFIX, '')
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
        -- Il moltiplicatore porta tutto nella unita' dichiarata dal catalogo
        -- (mln EUR -> mld EUR) e normalizza i segni dove la BCE usa convenzioni
        -- proprie (es. costo/ricavi riportato negativo).
        ROUND(n.valore_grezzo * c.moltiplicatore, 6) AS valore
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
