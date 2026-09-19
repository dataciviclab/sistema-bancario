-- mart_wd_indicators: Indicatori World Bank per paese/anno
-- Pivot degli indicatori principali

SELECT
    paese,
    codice_paese,
    anno,
    MAX(CASE WHEN codice_indicatore = 'FB.AST.NPER.ZS' THEN valore END) AS npl_ratio_pct,
    MAX(CASE WHEN codice_indicatore = 'FS.AST.PRVT.GD.ZS' THEN valore END) AS credito_pil_pct,
    MAX(CASE WHEN codice_indicatore = 'FB.CBK.BRCH.P5' THEN valore END) AS filiali_per_100k,
    MAX(CASE WHEN codice_indicatore = 'FB.ATM.TOTL.P5' THEN valore END) AS atm_per_100k,
    MAX(CASE WHEN codice_indicatore = 'FB.BNK.CAPA.ZS' THEN valore END) AS capitale_attivi_pct,
    MAX(CASE WHEN codice_indicatore = 'FB.AST.IRNR.ZS' THEN valore END) AS tasso_reale_pct,
    MAX(CASE WHEN codice_indicatore = 'FR.INR.LNDP' THEN valore END) AS spread_prestiti_pct
FROM clean_input
GROUP BY paese, codice_paese, anno
ORDER BY paese, anno
