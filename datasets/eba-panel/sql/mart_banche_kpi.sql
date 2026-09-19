-- mart_banche_kpi: KPI per banca/periodo

SELECT
    banca, nome_banca, paese, nome_paese, tipo_ssm, periodo,
    MAX(CASE WHEN codice_variabile = 'FECPHD0020' THEN valore END) AS cet1_ratio,
    MAX(CASE WHEN codice_variabile = 'FECPHD0029' THEN valore END) AS total_capital_ratio,
    MAX(CASE WHEN codice_variabile = 'FECPHD0025' THEN valore END) AS leverage_ratio,
    MAX(CASE WHEN codice_variabile = 'FECPHD01000' THEN valore END) AS roe,
    MAX(CASE WHEN codice_variabile = 'FECPHD01001' THEN valore END) AS return_tier1,
    MAX(CASE WHEN codice_variabile = 'FECPHD01005' THEN valore END) AS net_interest_margin,
    MAX(CASE WHEN codice_variabile = 'FECPHD00116' THEN valore END) AS total_assets
FROM clean_input
GROUP BY banca, nome_banca, paese, nome_paese, tipo_ssm, periodo
ORDER BY banca, periodo
