-- clean.sql: World Bank WDI — indicatori del settore finanziario
--
-- Il raw e' gia' in formato lungo (una riga per paese/indicatore/anno), scritto
-- da preprocess.py che interroga la v2 JSON API solo per i 7 indicatori usati.
--
-- Il clean precedente leggeva il bulk WDI_CSV.zip (~190 MB, ~1.400 indicatori)
-- e faceva UNNEST su 11 anni scritti a mano (2015-2025) mentre il registry
-- dichiarava 1960-2025: la storia non c'era e il download era 60x piu' grande
-- del necessario.

WITH raw AS (
    SELECT * FROM raw_input
)

SELECT
    CAST(paese AS VARCHAR) AS paese,
    CAST(codice_paese AS VARCHAR) AS codice_paese,
    CAST(indicatore AS VARCHAR) AS indicatore,
    CAST(codice_indicatore AS VARCHAR) AS codice_indicatore,
    CAST(anno AS INTEGER) AS anno,
    CAST(valore AS DOUBLE) AS valore,
    -- Aggregati World Bank: mondo, aree geografiche, fasce di reddito, unioni.
    -- Restano nel clean ma i mart li escludono.
    CAST(codice_paese AS VARCHAR) IN (
        'WLD', 'EUU', 'EMU', 'ARB', 'CSS', 'CEB', 'EAP', 'EAR', 'EAS', 'ECA', 'ECS', 'SSF',
        'HIC', 'HPC', 'IBD', 'IBT', 'IDA', 'IDB', 'IDX', 'LAC', 'LCN', 'LDC', 'LIC', 'LMC',
        'LTE', 'MIC', 'MNA', 'NAC', 'INX', 'OED', 'OSS', 'PRE', 'PST', 'SAS', 'SSA', 'TEA',
        'TEC', 'TLA', 'TMN', 'TSA', 'TSS', 'UMC', 'FCS', 'AFE', 'AFW', 'LAT', 'MEU', 'SXL'
    ) AS e_aggregato
FROM raw
WHERE codice_indicatore IS NOT NULL
  AND codice_paese IS NOT NULL
  AND valore IS NOT NULL
ORDER BY paese, codice_indicatore, anno
