-- mart_banche_kpi: KPI per banca e periodo
--
-- Una colonna = una serie dichiarata in series_catalog.csv.
-- Unita' omogenee: ratio in punti percentuali, attivo in miliardi.
-- `net_interest_margin` e' stato eliminato: la variabile EBA FECPHD01005 e'
-- definita "1 meno interessi attivi diviso interessi passivi", non un margine
-- (valori da -infinito a 8), quindi il nome era fuorviante.
--
-- ATTENZIONE: utile e margine operativo sono CUMULATI dall'inizio dell'anno
-- (YTD), non valori trimestrali. Il Q4 coincide con l'esercizio, il Q2 con il
-- semestre. Per questo il nome delle colonne porta `_ytd_`: sommare i quattro
-- trimestri darebbe un numero sbagliato di oltre tre volte.

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
        MAX(CASE WHEN metrica = 'attivo_totale' THEN valore END) AS attivo_totale_mld,
        MAX(CASE WHEN metrica = 'utile_netto_ytd' THEN valore END) AS utile_netto_ytd_mld,
        MAX(CASE WHEN metrica = 'margine_operativo_ytd' THEN valore END) AS margine_operativo_ytd_mld,
        MAX(CASE WHEN metrica = 'cost_of_risk' THEN valore END) AS cost_of_risk_pct,
        MAX(CASE WHEN metrica = 'return_on_rwa' THEN valore END) AS return_on_rwa_pct
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
    ROUND(attivo_totale_mld, 1) AS attivo_totale_mld,
    ROUND(utile_netto_ytd_mld, 1) AS utile_netto_ytd_mld,
    ROUND(margine_operativo_ytd_mld, 1) AS margine_operativo_ytd_mld,
    ROUND(cost_of_risk_pct, 2) AS cost_of_risk_pct,
    ROUND(return_on_rwa_pct, 2) AS return_on_rwa_pct
FROM serie
ORDER BY paese, banca, periodo
