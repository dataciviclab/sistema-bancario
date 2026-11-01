-- clean.sql: EBA Panel — dati per singola banca (Transparency Exercise)
--
-- Contratto: solo le serie dichiarate in series_catalog.csv.
--
-- Rispetto alla versione precedente questo clean NON butta piu' via:
--   * `country_long_code` -> paese_controparte: e' la dimensione che rende
--     possibile "quanta esposizione sovrana italiana ha Intesa";
--   * `lei_code`, `ssm`, `finrep` -> anagrafica e chiavi di aggancio;
--   * `country_long_rank` viene scartata: nel dataset di origine e' una colonna
--     spuria (contiene un'altra lista di paesi, non un rank).
--
-- Unita': i ratio EBA sono frazioni (0.1611) e vengono portati a punti
-- percentuali; gli importi sono in milioni e diventano miliardi. Il
-- moltiplicatore e' dichiarato nel catalogo, non sparso nelle query.

WITH catalogo AS (
    SELECT
        metrica,
        codice,
        classe_esposizione,
        descrizione,
        unita,
        CAST(moltiplicatore AS DOUBLE) AS moltiplicatore
    FROM read_csv('datasets/eba-panel/series_catalog.csv', header = true, auto_detect = true)
),

-- Il paese controparte arriva dalla fonte come nome inglese ("Italy"), mentre
-- `paese` e' ISO2 ("IT"). Senza questa mappa ogni consumatore dovrebbe
-- ricostruirla a mano: e' la prima trappola per chi legge il mart.
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
        -- Paese controparte: valorizzato solo per le serie "by country".
        -- Discriminante: il codice appartiene alla famiglia esposizioni/RWA.
        CASE
            WHEN CAST(code AS VARCHAR) IN (
                'FECPHD00294', 'FECPHD00297', 'FECPHD00299',
                'FECPHD00300', 'FECPHD00304', 'FECPHD00307',
                'FECPHD00376', 'FECPHD00379', 'FECPHD00382',
                'FECPHD00386', 'FECPHD00389'
            ) THEN CAST(country_long_code AS VARCHAR)
            ELSE NULL
        END AS paese_controparte,
        CAST(period AS INTEGER) AS periodo,
        -- Cadenza dichiarata: semestrale fino al 2017, trimestrale dal 2018.
        CASE WHEN CAST(period AS INTEGER) < 201801 THEN 'semestrale' ELSE 'trimestrale' END AS cadenza,
        CAST(amount AS DOUBLE) AS valore_grezzo
    FROM raw
    WHERE amount IS NOT NULL
)

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
    c.descrizione,
    c.unita,
    c.classe_esposizione,
    n.paese_controparte,
    p.codice_paese_controparte,
    COALESCE(p.e_aggregato, false) AS controparte_aggregata,
    ROUND(n.valore_grezzo * c.moltiplicatore, 6) AS valore
FROM normalizzato n
JOIN catalogo c ON n.codice = c.codice
LEFT JOIN paesi p ON n.paese_controparte = p.paese_controparte
ORDER BY c.metrica, n.banca, n.periodo
