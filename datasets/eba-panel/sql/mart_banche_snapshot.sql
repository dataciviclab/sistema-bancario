-- mart_banche_snapshot: Ultimo valore disponibile per banca/variabile

WITH ranked AS (
    SELECT
        banca, nome_banca, paese, nome_paese, tipo_ssm,
        codice_variabile, valore, periodo,
        ROW_NUMBER() OVER (PARTITION BY banca, codice_variabile ORDER BY periodo DESC) AS rn
    FROM clean_input
    WHERE codice_variabile IN (
        'FECPHD0020', 'FECPHD0029', 'FECPHD0025',
        'FECPHD01000', 'FECPHD01001', 'FECPHD01005',
        'FECPHD00116'
    )
),

latest AS (
    SELECT * FROM ranked WHERE rn = 1
)

SELECT
    banca, nome_banca, paese, nome_paese, tipo_ssm,
    MAX(CASE WHEN codice_variabile = 'FECPHD0020' THEN CAST(periodo AS VARCHAR) END) AS periodo_cet1,
    MAX(CASE WHEN codice_variabile = 'FECPHD01000' THEN CAST(periodo AS VARCHAR) END) AS periodo_roe,
    MAX(CASE WHEN codice_variabile = 'FECPHD0020' THEN valore END) AS cet1_ratio,
    MAX(CASE WHEN codice_variabile = 'FECPHD0029' THEN valore END) AS total_capital_ratio,
    MAX(CASE WHEN codice_variabile = 'FECPHD0025' THEN valore END) AS leverage_ratio,
    MAX(CASE WHEN codice_variabile = 'FECPHD01000' THEN valore END) AS roe,
    MAX(CASE WHEN codice_variabile = 'FECPHD01001' THEN valore END) AS return_tier1,
    MAX(CASE WHEN codice_variabile = 'FECPHD01005' THEN valore END) AS net_interest_margin,
    MAX(CASE WHEN codice_variabile = 'FECPHD00116' THEN valore END) AS total_assets
FROM latest
GROUP BY banca, nome_banca, paese, nome_paese, tipo_ssm
ORDER BY total_assets DESC NULLS LAST
