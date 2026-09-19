-- mart_wd_snapshot: Ultimo anno disponibile per paese
-- Pivot da clean_input (dati unpivoted)

WITH pivoted AS (
    SELECT
        paese, codice_paese, anno,
        MAX(CASE WHEN codice_indicatore = 'FB.AST.NPER.ZS' THEN valore END) AS npl_ratio_pct,
        MAX(CASE WHEN codice_indicatore = 'FS.AST.PRVT.GD.ZS' THEN valore END) AS credito_pil_pct,
        MAX(CASE WHEN codice_indicatore = 'FB.CBK.BRCH.P5' THEN valore END) AS filiali_per_100k,
        MAX(CASE WHEN codice_indicatore = 'FB.ATM.TOTL.P5' THEN valore END) AS atm_per_100k,
        MAX(CASE WHEN codice_indicatore = 'FB.BNK.CAPA.ZS' THEN valore END) AS capitale_attivi_pct,
        MAX(CASE WHEN codice_indicatore = 'FB.AST.IRNR.ZS' THEN valore END) AS tasso_reale_pct,
        MAX(CASE WHEN codice_indicatore = 'FR.INR.LNDP' THEN valore END) AS spread_prestiti_pct,
        ROW_NUMBER() OVER (PARTITION BY paese ORDER BY anno DESC) AS rn
    FROM clean_input
    GROUP BY paese, codice_paese, anno
)
SELECT
    paese, codice_paese, anno,
    npl_ratio_pct, credito_pil_pct, filiali_per_100k, atm_per_100k,
    capitale_attivi_pct, tasso_reale_pct, spread_prestiti_pct
FROM pivoted
WHERE rn = 1
ORDER BY paese
