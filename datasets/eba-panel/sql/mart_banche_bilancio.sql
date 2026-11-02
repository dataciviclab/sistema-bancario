-- mart_banche_bilancio: da dove viene il rischio e com'e' fatto l'attivo
--
-- Una riga = banca x periodo. Tre letture:
--   1. RWA per tipo di rischio: quanta parte del capitale assorbito viene dal
--      credito, dal mercato, dall'operativo;
--   2. attivo per criterio di valutazione: quanto e' a fair value (e quindi
--      esposto alle oscillazioni dei prezzi, titoli di Stato compresi) e quanto
--      al costo ammortizzato;
--   3. prestiti per stage IFRS 9: lo stage 2 e' il segnale anticipato di
--      deterioramento, prima che il credito diventi sofferenza (stage 3).
--
-- Nota sul dataset di origine: per alcune voci (attivita' finanziarie, RWA per
-- credito) la stessa banca/periodo/codice compare piu' volte con importi
-- diversi, senza una dimensione che li distingua (fino al 96% delle celle per
-- l'HFT). Il valore aggregato e' il maggiore; sommare gonfierebbe l'attivo
-- finanziario oltre l'attivo totale, cosa impossibile per costruzione. Qui si
-- usa MAX e un test verifica che l'attivo finanziario resti sotto l'attivo.
--
-- `attivo_fvpl` somma due serie (fair value obbligatorio e designato), per
-- questo usa MAX(...) + MAX(...) e non un'unica espressione.

WITH serie AS (
    SELECT
        banca,
        nome_banca,
        paese,
        periodo,
        MAX(CASE WHEN metrica = 'rwa_totale' THEN valore END) AS rwa_totale_mld,
        MAX(CASE WHEN metrica = 'rwa_credito' THEN valore END) AS rwa_credito_mld,
        MAX(CASE WHEN metrica = 'rwa_mercato' THEN valore END) AS rwa_mercato_mld,
        MAX(CASE WHEN metrica = 'rwa_operativo' THEN valore END) AS rwa_operativo_mld,
        MAX(CASE WHEN metrica = 'rwa_cva' THEN valore END) AS rwa_cva_mld,
        MAX(CASE WHEN metrica = 'rwa_cartolarizzazioni' THEN valore END) AS rwa_cartolarizzazioni_mld,
        -- Attivo a fair value = somma delle quattro categorie (ognuna dedup. con MAX)
        COALESCE(MAX(CASE WHEN metrica = 'attivo_hft' THEN valore END), 0)
          + COALESCE(MAX(CASE WHEN metrica = 'attivo_oci' THEN valore END), 0)
          + COALESCE(MAX(CASE WHEN metrica = 'attivo_fvpl' THEN valore END), 0)
          + COALESCE(MAX(CASE WHEN metrica = 'attivo_fvpl_designato' THEN valore END), 0)
            AS attivo_fair_value_mld,
        MAX(CASE WHEN metrica = 'attivo_costo_ammortizzato' THEN valore END) AS attivo_costo_ammortizzato_mld,
        MAX(CASE WHEN metrica = 'prestiti_stage1' THEN valore END) AS prestiti_stage1_mld,
        MAX(CASE WHEN metrica = 'prestiti_stage2' THEN valore END) AS prestiti_stage2_mld,
        MAX(CASE WHEN metrica = 'prestiti_stage3' THEN valore END) AS prestiti_stage3_mld,
        MAX(CASE WHEN metrica = 'impairment_stage3' THEN valore END) AS impairment_stage3_mld
    FROM clean_input
    WHERE paese_controparte IS NULL
      AND metrica IN (
          'rwa_totale', 'rwa_credito', 'rwa_mercato', 'rwa_operativo', 'rwa_cva',
          'rwa_cartolarizzazioni', 'attivo_hft', 'attivo_oci', 'attivo_fvpl',
          'attivo_fvpl_designato', 'attivo_costo_ammortizzato',
          'prestiti_stage1', 'prestiti_stage2', 'prestiti_stage3', 'impairment_stage3'
      )
    GROUP BY banca, nome_banca, paese, periodo
),

calcolato AS (
    SELECT
        *,
        attivo_fair_value_mld + attivo_costo_ammortizzato_mld AS attivo_finanziario_mld,
        COALESCE(prestiti_stage1_mld, 0) + COALESCE(prestiti_stage2_mld, 0) + COALESCE(prestiti_stage3_mld, 0)
            AS prestiti_lordi_mld
    FROM serie
)

SELECT
    banca,
    nome_banca,
    paese,
    periodo,
    ROUND(rwa_totale_mld, 1) AS rwa_totale_mld,
    ROUND(rwa_credito_mld, 1) AS rwa_credito_mld,
    ROUND(rwa_mercato_mld, 1) AS rwa_mercato_mld,
    ROUND(rwa_operativo_mld, 1) AS rwa_operativo_mld,
    ROUND(rwa_cva_mld, 1) AS rwa_cva_mld,
    ROUND(rwa_cartolarizzazioni_mld, 1) AS rwa_cartolarizzazioni_mld,
    ROUND(rwa_credito_mld / NULLIF(rwa_totale_mld, 0) * 100, 1) AS quota_rwa_credito_pct,
    ROUND(rwa_mercato_mld / NULLIF(rwa_totale_mld, 0) * 100, 1) AS quota_rwa_mercato_pct,
    ROUND(rwa_operativo_mld / NULLIF(rwa_totale_mld, 0) * 100, 1) AS quota_rwa_operativo_pct,
    ROUND(attivo_fair_value_mld, 1) AS attivo_fair_value_mld,
    ROUND(attivo_costo_ammortizzato_mld, 1) AS attivo_costo_ammortizzato_mld,
    ROUND(attivo_finanziario_mld, 1) AS attivo_finanziario_mld,
    ROUND(attivo_fair_value_mld / NULLIF(attivo_finanziario_mld, 0) * 100, 1) AS quota_fair_value_pct,
    ROUND(prestiti_lordi_mld, 1) AS prestiti_lordi_mld,
    ROUND(prestiti_stage2_mld / NULLIF(prestiti_lordi_mld, 0) * 100, 2) AS prestiti_stage2_pct,
    ROUND(prestiti_stage3_mld / NULLIF(prestiti_lordi_mld, 0) * 100, 2) AS prestiti_stage3_pct,
    -- Le rettifiche sono riportate con segno negativo: la copertura e' il loro valore assoluto
    ROUND(ABS(impairment_stage3_mld) / NULLIF(prestiti_stage3_mld, 0) * 100, 1) AS copertura_stage3_pct
FROM calcolato
WHERE rwa_totale_mld IS NOT NULL OR attivo_fair_value_mld IS NOT NULL
ORDER BY paese, banca, periodo
