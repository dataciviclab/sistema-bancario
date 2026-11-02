-- mart_esposizioni: dove sono esposte le banche, per paese controparte
--
-- Una riga = banca x paese controparte x periodo, con i due metodi
-- regolamentari (SA e IRB) gia' sommati. Sommare e' corretto: una posizione
-- ricade in un metodo o nell'altro, non in entrambi.
--
-- Perche' il metodo conta: pubblicare solo SA (come nella prima versione)
-- sottostimava l'esposizione delle banche che usano modelli interni. Per
-- Intesa verso l'Italia l'IRB vale 252 mld su 420, e la quota sovrana scende
-- dal 77% (solo SA) al 32% (SA+IRB). Il dettaglio per metodo e' in
-- mart_esposizioni_metodo.
--
-- `esposizione_totale_mld` somma TUTTE le classi dichiarate, non solo le sei
-- principali: le classi minori (CIU, covered bond, mutui ipotecari, enti
-- locali, ecc.) confluiscono in `esposizione_altre_classi_mld` e quindi nel
-- totale, cosi' il denominatore delle quote e' completo.

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
        SUM(CASE WHEN metrica = 'esposizione_sovrana' THEN valore END) AS esposizione_sovrana_mld,
        SUM(CASE WHEN metrica = 'esposizione_imprese' THEN valore END) AS esposizione_imprese_mld,
        SUM(CASE WHEN metrica = 'esposizione_retail' THEN valore END) AS esposizione_retail_mld,
        SUM(CASE WHEN metrica = 'esposizione_istituzioni' THEN valore END) AS esposizione_istituzioni_mld,
        SUM(CASE WHEN metrica = 'esposizione_equity' THEN valore END) AS esposizione_equity_mld,
        SUM(CASE WHEN metrica = 'esposizione_altro' THEN valore END) AS esposizione_altro_mld,
        SUM(CASE WHEN metrica = 'esposizione_altre_classi' THEN valore END) AS esposizione_altre_classi_mld,
        SUM(CASE WHEN metrica = 'rwa_sovrana' THEN valore END) AS rwa_sovrana_mld,
        SUM(CASE WHEN metrica = 'rwa_imprese' THEN valore END) AS rwa_imprese_mld,
        SUM(CASE WHEN metrica = 'rwa_retail' THEN valore END) AS rwa_retail_mld,
        SUM(CASE WHEN metrica = 'rwa_istituzioni' THEN valore END) AS rwa_istituzioni_mld,
        SUM(CASE WHEN metrica = 'rwa_equity' THEN valore END) AS rwa_equity_mld,
        SUM(CASE WHEN metrica = 'rwa_altro' THEN valore END) AS rwa_altro_mld,
        SUM(CASE WHEN metrica = 'rwa_altre_classi' THEN valore END) AS rwa_altre_classi_mld
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
          + COALESCE(esposizione_altro_mld, 0)
          + COALESCE(esposizione_altre_classi_mld, 0) AS esposizione_totale_mld,
        COALESCE(rwa_sovrana_mld, 0)
          + COALESCE(rwa_imprese_mld, 0)
          + COALESCE(rwa_retail_mld, 0)
          + COALESCE(rwa_istituzioni_mld, 0)
          + COALESCE(rwa_equity_mld, 0)
          + COALESCE(rwa_altro_mld, 0)
          + COALESCE(rwa_altre_classi_mld, 0) AS rwa_totale_mld
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
    ROUND(esposizione_altre_classi_mld, 1) AS esposizione_altre_classi_mld,
    ROUND(esposizione_totale_mld, 1) AS esposizione_totale_mld,
    ROUND(rwa_sovrana_mld, 1) AS rwa_sovrana_mld,
    ROUND(rwa_imprese_mld, 1) AS rwa_imprese_mld,
    ROUND(rwa_retail_mld, 1) AS rwa_retail_mld,
    ROUND(rwa_istituzioni_mld, 1) AS rwa_istituzioni_mld,
    ROUND(rwa_equity_mld, 1) AS rwa_equity_mld,
    ROUND(rwa_altro_mld, 1) AS rwa_altro_mld,
    ROUND(rwa_altre_classi_mld, 1) AS rwa_altre_classi_mld,
    ROUND(rwa_totale_mld, 1) AS rwa_totale_mld,
    ROUND(esposizione_sovrana_mld / NULLIF(esposizione_totale_mld, 0) * 100, 1) AS quota_sovrana_pct,
    ROUND(rwa_totale_mld / NULLIF(esposizione_totale_mld, 0) * 100, 2) AS densita_rwa_pct
FROM totali
-- Righe con esposizione totale arrotondata a zero: la controparte compare nel
-- dataset EBA ma senza importo. Non aggiungono informazione e sporcano i conteggi.
WHERE ROUND(esposizione_totale_mld, 1) > 0
ORDER BY banca, periodo, paese_controparte
