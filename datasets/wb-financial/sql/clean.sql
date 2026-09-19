-- clean.sql: World Bank WDI Financial Sector
-- CSV ha 4 righe di header. DuckDB le salta con header=true.
-- Anni: colonne `1960` a `2025`

SELECT
    "Country Name" AS paese,
    "Country Code" AS codice_paese,
    "Indicator Name" AS indicatore,
    "Indicator Code" AS codice_indicatore,
    CAST(anno AS INTEGER) AS anno,
    CAST(valore AS DOUBLE) AS valore
FROM (
    SELECT
        "Country Name", "Country Code", "Indicator Name", "Indicator Code",
        UNNEST(['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']) AS anno,
        UNNEST([
            "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"
        ]) AS valore
    FROM raw_input
    WHERE "Country Code" IS NOT NULL
      AND "Indicator Code" IS NOT NULL
      AND "Country Name" != 'Country Name'
)
WHERE valore IS NOT NULL
  AND codice_indicatore IN (
      'FB.AST.NPER.ZS',    -- NPL ratio
      'FS.AST.PRVT.GD.ZS', -- Credito privato/PIL
      'FB.CBK.BRCH.P5',    -- Filiali bancarie per 100k
      'FB.ATM.TOTL.P5',    -- ATM per 100k
      'FB.BNK.CAPA.ZS',    -- Capitale bancario/attivi
      'FB.AST.IRNR.ZS',    -- Tasso interesse reale
      'FR.INR.LNDP'        -- Spread prestiti-depositi
  )
ORDER BY paese, codice_indicatore, anno
