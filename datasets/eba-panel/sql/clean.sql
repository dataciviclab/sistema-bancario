-- clean.sql: EBA Panel — dati per singola banca (Transparency Exercise)
--
-- Contratto: solo le serie dichiarate in series_catalog.csv.
--
-- Tre cose che questo clean tiene e che la versione precedente perdeva:
--   1. `metodo` (SA / IRB): la stessa esposizione e' pubblicata con due approcci
--      regolamentari. Usare solo SA sottostima le banche che usano modelli
--      interni (per alcune vale oltre l'80% dell'esposizione).
--   2. `classe_esposizione`, per distinguere sovrana, imprese, retail, ecc.
--      e per aggregare le classi minori in un residuo esplicito.
--   3. `country_long_code` -> paese_controparte, con il codice ISO2 dal codelist.
--
-- Scartata di proposito: `country_long_rank` (colonna spuria del dataset di
-- origine: contiene un'altra lista di paesi) e le famiglie di sotto-dettaglio
-- (SME, Retail type, Retail non-SME, Corp. SL), che duplicano le classi
-- principali e gonfierebbero i totali.

WITH catalogo AS (
    SELECT
        metrica,
        codice,
        metodo,
        classe_esposizione,
        descrizione,
        unita,
        CAST(moltiplicatore AS DOUBLE) AS moltiplicatore
    FROM read_csv('datasets/eba-panel/series_catalog.csv', header = true, auto_detect = true)
),

paesi AS (
    SELECT
        paese_controparte,
        NULLIF(codice_paese_controparte, '') AS codice_paese_controparte,
        CAST(e_aggregato AS BOOLEAN) AS e_aggregato
    FROM read_csv('datasets/eba-panel/codelists/paesi_controparte.csv', header = true, auto_detect = true)
),

raw AS (
    SELECT * FROM raw_input
),

normalizzato AS (
    SELECT
        CAST(abbreviation AS VARCHAR) AS banca,
        CAST(name_short AS VARCHAR) AS nome_banca,
        CAST(bank_name AS VARCHAR) AS nome_legale,
        CAST(country AS VARCHAR) AS paese,
        CAST(desc_country AS VARCHAR) AS nome_paese,
        CAST(ssm AS VARCHAR) AS tipo_ssm,
        CAST(finrep AS VARCHAR) AS finrep,
        CAST(lei_code AS VARCHAR) AS lei,
        CAST(code AS VARCHAR) AS codice,
        CAST(period AS INTEGER) AS periodo,
        CASE WHEN CAST(period AS INTEGER) < 201801 THEN 'semestrale' ELSE 'trimestrale' END AS cadenza,
        CAST(amount AS DOUBLE) AS valore_grezzo,
        -- Il paese controparte esiste solo per le serie "by country": lo decide
        -- il catalogo, non una lista di codici scritta a mano.
        CASE
            WHEN CAST(code AS VARCHAR) IN (
                SELECT codice FROM catalogo WHERE classe_esposizione IS NOT NULL
            ) THEN CAST(country_long_code AS VARCHAR)
            ELSE NULL
        END AS paese_controparte
    FROM raw
    WHERE amount IS NOT NULL
),

arricchito AS (
    SELECT
        n.banca,
        n.nome_banca,
        n.nome_legale,
        n.paese,
        n.nome_paese,
        n.tipo_ssm,
        n.finrep,
        n.lei,
        n.periodo,
        n.cadenza,
        c.metrica,
        c.metodo,
        c.classe_esposizione,
        c.descrizione,
        c.unita,
        n.paese_controparte,
        p.codice_paese_controparte,
        COALESCE(p.e_aggregato, false) AS controparte_aggregata,
        ROUND(n.valore_grezzo * c.moltiplicatore, 6) AS valore,
        -- Quante righe di origine alimentano la stessa banca/periodo/serie.
        -- Il dataset EBA riporta piu' osservazioni per la stessa cella: alcune
        -- sono un totale seguito dalle sue componenti, altre sono entita'
        -- diverse con lo stesso LEI master. Serve per l'audit e per i test.
        COUNT(*) OVER (PARTITION BY n.banca, n.periodo, c.metrica) AS voci_origine
    FROM normalizzato n
    JOIN catalogo c ON n.codice = c.codice
    LEFT JOIN paesi p ON n.paese_controparte = p.paese_controparte
)

SELECT
    banca,
    nome_banca,
    nome_legale,
    paese,
    nome_paese,
    tipo_ssm,
    finrep,
    lei,
    periodo,
    cadenza,
    metrica,
    metodo,
    classe_esposizione,
    descrizione,
    unita,
    paese_controparte,
    codice_paese_controparte,
    controparte_aggregata,
    valore,
    voci_origine
FROM arricchito
ORDER BY metrica, banca, periodo
