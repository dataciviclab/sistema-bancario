-- mart_banche_snapshot: ultimo valore disponibile per banca e variabile
--
-- Le variabili hanno ritardi di pubblicazione diversi (CET1 e ROE non sono
-- ancora disponibili per il 2025), quindi ogni colonna porta con se' il
-- periodo a cui si riferisce: `periodo_cet1`, `periodo_roe`, ecc.

WITH ranked AS (
    SELECT
        banca,
        nome_banca,
        paese,
        nome_paese,
        tipo_ssm,
        metrica,
        valore,
        periodo,
        ROW_NUMBER() OVER (PARTITION BY banca, metrica ORDER BY periodo DESC) AS rn
    FROM clean_input
    WHERE paese_controparte IS NULL
),

latest AS (
    SELECT * FROM ranked WHERE rn = 1
)

SELECT
    banca,
    nome_banca,
    paese,
    nome_paese,
    tipo_ssm,
    MAX(CASE WHEN metrica = 'attivo_totale' THEN CAST(periodo AS VARCHAR) END) AS periodo_attivo,
    MAX(CASE WHEN metrica = 'cet1' THEN CAST(periodo AS VARCHAR) END) AS periodo_cet1,
    MAX(CASE WHEN metrica = 'roe' THEN CAST(periodo AS VARCHAR) END) AS periodo_roe,
    MAX(CASE WHEN metrica = 'attivo_totale' THEN ROUND(valore, 1) END) AS attivo_totale_mld,
    MAX(CASE WHEN metrica = 'cet1' THEN ROUND(valore, 2) END) AS cet1_pct,
    MAX(CASE WHEN metrica = 'capitale_totale' THEN ROUND(valore, 2) END) AS capitale_totale_pct,
    MAX(CASE WHEN metrica = 'leverage' THEN ROUND(valore, 2) END) AS leverage_pct,
    MAX(CASE WHEN metrica = 'roe' THEN ROUND(valore, 2) END) AS roe_pct,
    MAX(CASE WHEN metrica = 'return_tier1' THEN ROUND(valore, 2) END) AS return_tier1_pct
FROM latest
GROUP BY banca, nome_banca, paese, nome_paese, tipo_ssm
ORDER BY attivo_totale_mld DESC NULLS LAST
