-- clean.sql: EBA Panel — Dati per singola banca
-- Estrae i KPI chiave dal formato long (banca x periodo x variabile)

WITH raw AS (
    SELECT * FROM raw_input
),

-- Filtra solo le variabili chiave
filtered AS (
    SELECT
        abbreviation AS banca,
        name_short AS nome_banca,
        bank_name AS nome_legale,
        country AS paese,
        desc_country AS nome_paese,
        ssm AS tipo_ssm,
        period AS periodo,
        code AS codice_variabile,
        name AS nome_variabile,
        amount AS valore
    FROM raw
    WHERE code IN (
        'FECPHD0020',  -- CET1 ratio (fully loaded)
        'FECPHD0029',  -- Total capital ratio
        'FECPHD0025',  -- Leverage ratio
        'FECPHD01000', -- Return on equity
        'FECPHD01001', -- Return on Tier 1 capital
        'FECPHD01005', -- Net interest margin
        'FECPHD00116', -- Total assets
        'FECPHD00117', -- Total assets (alt)
        'FECPHD01024', -- Log CET1 amount
        'FECPHD01026', -- Log Tier 1 amount
        'FECPHD01031', -- RWA IRB Corporates
        'FECPHD00389', -- RWA by country SA Retail
        'FECPHD00212', -- Original exposure SME
        'FECPHD00294', -- Exposure value by country SA Central gov
        'FECPHD00297', -- Exposure value by country SA Corporates
        'FECPHD00307', -- Exposure value by country SA Retail
        'FECPHD00299', -- Exposure value by country SA Equity
        'FECPHD00304', -- Exposure value by country SA Other
        'FECPHD00376', -- RWA by country SA Central gov
        'FECPHD00379', -- RWA by country SA Corporates
        'FECPHD00382', -- RWA by country SA Institutions
        'FECPHD00386', -- RWA by country SA Other
        'FECPHD00389', -- RWA by country SA Retail
        'FECPHD01031', -- RWA IRB Corporates
        'FECPHD00300', -- Exposure value by country SA Institutions
        'FECPHD00212', -- Original exposure SME
        'FECPHD00195', -- Original exposure by country SA Corporates
        'FECPHD00193', -- Original exposure by country SA Claims CIU
        'FECPHD00314', -- Exposure value by country SME SA Corporates SME
        'FECPHD00396', -- RWA by country SME SA Corporates SME
        'FECPHD01032', -- RWA defaulted IRB Corporates
        'FECPHD01031'  -- RWA IRB Corporates
    )
    AND amount IS NOT NULL
)

SELECT
    banca,
    nome_banca,
    nome_legale,
    paese,
    nome_paese,
    tipo_ssm,
    CAST(periodo AS INTEGER) AS periodo,
    codice_variabile,
    nome_variabile,
    CAST(valore AS DOUBLE) AS valore
FROM filtered
ORDER BY banca, periodo, codice_variabile
