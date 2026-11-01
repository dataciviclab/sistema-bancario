-- mart_banche_kpi: KPI per banca e periodo
--
-- Una colonna = una serie dichiarata in series_catalog.csv.
-- Unita' omogenee: ratio in punti percentuali, attivo in miliardi.
-- `net_interest_margin` e' stato eliminato: la variabile EBA FECPHD01005 e'
-- definita "1 meno interessi attivi diviso interessi passivi", non un margine
-- (valori da -infinito a 8), quindi il nome era fuorviante.

WITH serie AS (
    SELECT
        banca,
        nome_banca,
        paese,
        nome_paese,
        tipo_ssm,
        periodo,
        cadenza,
        MAX(CASE WHEN metrica = 'cet1' THEN valore END) AS cet1_pct,
        MAX(CASE WHEN metrica = 'capitale_totale' THEN valore END) AS capitale_totale_pct,
        MAX(CASE WHEN metrica = 'leverage' THEN valore END) AS leverage_pct,
        MAX(CASE WHEN metrica = 'roe' THEN valore END) AS roe_pct,
        MAX(CASE WHEN metrica = 'return_tier1' THEN valore END) AS return_tier1_pct,
        MAX(CASE WHEN metrica = 'attivo_totale' THEN valore END) AS attivo_totale_mld
    FROM clean_input
    WHERE paese_controparte IS NULL
    GROUP BY banca, nome_banca, paese, nome_paese, tipo_ssm, periodo, cadenza
)

SELECT
    banca,
    nome_banca,
    paese,
    nome_paese,
    tipo_ssm,
    periodo,
    cadenza,
    ROUND(cet1_pct, 2) AS cet1_pct,
    ROUND(capitale_totale_pct, 2) AS capitale_totale_pct,
    ROUND(leverage_pct, 2) AS leverage_pct,
    ROUND(roe_pct, 2) AS roe_pct,
    ROUND(return_tier1_pct, 2) AS return_tier1_pct,
    ROUND(attivo_totale_mld, 1) AS attivo_totale_mld
FROM serie
ORDER BY paese, banca, periodo
