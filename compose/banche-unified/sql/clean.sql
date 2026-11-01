-- clean.sql — Compose: unifica KPI bancari + bilanci + tassi
--
-- Sorgenti: mart ecb_cbd2 (raw_input) + clean ecb-bsi + clean ecb-mir.
-- I clean di BSI e MIR sono gia' in formato lungo con una colonna `metrica`
-- (serie dichiarate in series_catalog.csv) e valori gia' normalizzati:
-- BSI in miliardi EUR, MIR in punti percentuali. Qui si fa solo il pivot,
-- senza AVG su dimensioni eterogenee.

WITH cbd2 AS (
    SELECT
        paese, anno, trimestre,
        roe_pct, roa_pct, costo_reddito_pct, margine_interesse_pct,
        cet1_pct, tier1_pct,
        npl_ratio_pct, copertura_npl_pct,
        lcr_pct, prestiti_deposits_pct, prestiti_attivo_pct
    FROM raw_input
),

bsi AS (
    SELECT
        paese,
        anno,
        trimestre,
        MAX(CASE WHEN metrica = 'attivo_totale' THEN valore END) AS attivo_totale_mld,
        MAX(CASE WHEN metrica = 'prestiti' THEN valore END) AS prestiti_mld,
        MAX(CASE WHEN metrica = 'depositi' THEN valore END) AS deposits_mld
    FROM read_parquet('{support.bsi_balance.clean}')
    WHERE trimestre IS NOT NULL
    GROUP BY paese, anno, trimestre
),

mir AS (
    SELECT
        paese,
        anno,
        trimestre,
        AVG(CASE WHEN metrica = 'tasso_mutuo' THEN valore END) AS tasso_mutuo_pct,
        AVG(CASE WHEN metrica = 'tasso_imprese' THEN valore END) AS tasso_imprese_pct,
        AVG(CASE WHEN metrica = 'tasso_depositi_scadenza' THEN valore END) AS tasso_depositi_scadenza_pct
    FROM read_parquet('{support.mir_rates.clean}')
    WHERE trimestre IS NOT NULL
    GROUP BY paese, anno, trimestre
)

SELECT
    c.paese,
    c.anno,
    c.trimestre,
    -- KPI bancari (CBD2)
    c.roe_pct,
    c.roa_pct,
    c.costo_reddito_pct,
    c.margine_interesse_pct,
    c.cet1_pct,
    c.tier1_pct,
    c.npl_ratio_pct,
    c.copertura_npl_pct,
    c.lcr_pct,
    -- Bilanci MFI (BSI, miliardi EUR)
    ROUND(bsi.attivo_totale_mld, 1) AS attivo_totale_mld,
    ROUND(bsi.prestiti_mld, 1) AS prestiti_mld,
    ROUND(bsi.deposits_mld, 1) AS deposits_mld,
    -- Tassi (MIR, % annuo)
    ROUND(mir.tasso_mutuo_pct, 2) AS tasso_mutuo_pct,
    ROUND(mir.tasso_imprese_pct, 2) AS tasso_imprese_pct,
    ROUND(mir.tasso_depositi_scadenza_pct, 2) AS tasso_depositi_scadenza_pct
FROM cbd2 c
LEFT JOIN bsi ON c.paese = bsi.paese AND c.anno = bsi.anno AND c.trimestre = bsi.trimestre
LEFT JOIN mir ON c.paese = mir.paese AND c.anno = mir.anno AND c.trimestre = mir.trimestre
ORDER BY c.paese, c.anno, c.trimestre
