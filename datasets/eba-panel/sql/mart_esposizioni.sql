-- mart_esposizioni: dove sono esposte le banche, per paese controparte
--
-- Una riga = banca x paese controparte x periodo. Le colonne sono le classi
-- di esposizione dichiarate in series_catalog.csv, con il rispettivo RWA.
--
-- Perche' conta: la stessa tabella risponde a due domande diverse.
--   1. "Chi finanzia lo Stato?" -> esposizione_sovrana_mld, letta insieme ai
--      dati di debito pubblico.
--   2. "Dove sta il rischio geografico?" -> quota delle classi per paese.
--
-- Nota: `country_long_rank` del dataset di origine e' una colonna spuria
-- (contiene un'altra lista di paesi) ed e' esclusa nel clean.
--
-- `paese_controparte` e' il nome inglese della fonte; `codice_paese_controparte`
-- e' l'ISO2 per i join. Le voci che non sono paesi ("Other", "International
-- organisations") hanno `controparte_aggregata = true`: chi legge deve escluderle
-- oppure dichiararle.

WITH serie AS (
    SELECT
        banca,
        nome_banca,
        nome_legale,
        paese,
        periodo,
        paese_controparte,
        codice_paese_controparte,
        controparte_aggregata,
        MAX(CASE WHEN metrica = 'esposizione_sovrana' THEN valore END) AS esposizione_sovrana_mld,
        MAX(CASE WHEN metrica = 'esposizione_imprese' THEN valore END) AS esposizione_imprese_mld,
        MAX(CASE WHEN metrica = 'esposizione_retail' THEN valore END) AS esposizione_retail_mld,
        MAX(CASE WHEN metrica = 'esposizione_istituzioni' THEN valore END) AS esposizione_istituzioni_mld,
        MAX(CASE WHEN metrica = 'esposizione_equity' THEN valore END) AS esposizione_equity_mld,
        MAX(CASE WHEN metrica = 'esposizione_altro' THEN valore END) AS esposizione_altro_mld,
        MAX(CASE WHEN metrica = 'rwa_sovrana' THEN valore END) AS rwa_sovrana_mld,
        MAX(CASE WHEN metrica = 'rwa_imprese' THEN valore END) AS rwa_imprese_mld,
        MAX(CASE WHEN metrica = 'rwa_retail' THEN valore END) AS rwa_retail_mld,
        MAX(CASE WHEN metrica = 'rwa_istituzioni' THEN valore END) AS rwa_istituzioni_mld,
        MAX(CASE WHEN metrica = 'rwa_altro' THEN valore END) AS rwa_altro_mld
    FROM clean_input
    WHERE paese_controparte IS NOT NULL
    GROUP BY banca, nome_banca, nome_legale, paese, periodo, paese_controparte,
             codice_paese_controparte, controparte_aggregata
),

totali AS (
    SELECT
        *,
        COALESCE(esposizione_sovrana_mld, 0)
          + COALESCE(esposizione_imprese_mld, 0)
          + COALESCE(esposizione_retail_mld, 0)
          + COALESCE(esposizione_istituzioni_mld, 0)
          + COALESCE(esposizione_equity_mld, 0)
          + COALESCE(esposizione_altro_mld, 0) AS esposizione_totale_mld,
        COALESCE(rwa_sovrana_mld, 0)
          + COALESCE(rwa_imprese_mld, 0)
          + COALESCE(rwa_retail_mld, 0)
          + COALESCE(rwa_istituzioni_mld, 0)
          + COALESCE(rwa_altro_mld, 0) AS rwa_totale_mld
    FROM serie
)

SELECT
    banca,
    nome_banca,
    nome_legale,
    paese,
    periodo,
    paese_controparte,
    codice_paese_controparte,
    controparte_aggregata,
    ROUND(esposizione_sovrana_mld, 1) AS esposizione_sovrana_mld,
    ROUND(esposizione_imprese_mld, 1) AS esposizione_imprese_mld,
    ROUND(esposizione_retail_mld, 1) AS esposizione_retail_mld,
    ROUND(esposizione_istituzioni_mld, 1) AS esposizione_istituzioni_mld,
    ROUND(esposizione_equity_mld, 1) AS esposizione_equity_mld,
    ROUND(esposizione_altro_mld, 1) AS esposizione_altro_mld,
    ROUND(esposizione_totale_mld, 1) AS esposizione_totale_mld,
    ROUND(rwa_sovrana_mld, 1) AS rwa_sovrana_mld,
    ROUND(rwa_imprese_mld, 1) AS rwa_imprese_mld,
    ROUND(rwa_retail_mld, 1) AS rwa_retail_mld,
    ROUND(rwa_istituzioni_mld, 1) AS rwa_istituzioni_mld,
    ROUND(rwa_altro_mld, 1) AS rwa_altro_mld,
    ROUND(rwa_totale_mld, 1) AS rwa_totale_mld,
    ROUND(esposizione_sovrana_mld / NULLIF(esposizione_totale_mld, 0) * 100, 1) AS quota_sovrana_pct,
    ROUND(rwa_totale_mld / NULLIF(esposizione_totale_mld, 0) * 100, 2) AS densita_rwa_pct
FROM totali
-- Righe con esposizione totale arrotondata a zero: la controparte compare nel
-- dataset EBA ma senza importo. Non aggiungono informazione e sporcano i conteggi.
WHERE ROUND(esposizione_totale_mld, 1) > 0
ORDER BY banca, periodo, paese_controparte
