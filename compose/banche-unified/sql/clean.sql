-- clean.sql — Compose: unifica KPI bancari + bilanci + tassi
-- Legge da raw_input (CBD2) e JOIN con support datasets (BSI, MIR)
-- BSI e MIR sono unpivoted: pivota prima del JOIN

WITH cbd2 AS (
    SELECT
        paese, anno, trimestre,
        roe_pct, roa_pct, costo_reddito_pct, margine_interesse_pct,
        cet1_pct, tier1_pct,
        npl_ratio_pct, copertura_npl_pct,
        lcr_pct, prestiti_deposits_pct, prestiti_attivo_pct
    FROM raw_input
),

bsi_raw AS (
    SELECT * FROM read_parquet('{support.bsi_balance.clean}')
),

bsi AS (
    SELECT
        paese, anno, trimestre,
        ROUND(AVG(CASE WHEN voce = 'T00' THEN valore / 1000 END), 1) AS attivo_totale_mld,
        ROUND(AVG(CASE WHEN voce = 'A20T' THEN valore / 1000 END), 1) AS prestiti_mld,
        ROUND(AVG(CASE WHEN voce = 'L20' THEN valore / 1000 END), 1) AS deposits_mld,
        ROUND(AVG(CASE WHEN voce = 'L40' THEN valore / 1000 END), 1) AS obbligazioni_mld,
        ROUND(AVG(CASE WHEN voce = 'L60' THEN valore / 1000 END), 1) AS capitale_mld
    FROM bsi_raw
    WHERE frequenza = 'Q' OR (frequenza = 'M' AND trimestre IS NOT NULL)
    GROUP BY paese, anno, trimestre
),

mir_raw AS (
    SELECT * FROM read_parquet('{support.mir_rates.clean}')
),

mir AS (
    SELECT
        paese, anno, trimestre,
        ROUND(AVG(CASE WHEN voce = 'A2C' AND scadenza = 'A' THEN valore END), 2) AS tasso_mutuo_pct,
        ROUND(AVG(CASE WHEN voce = 'A2C' AND scadenza = 'F' THEN valore END), 2) AS tasso_mutuo_variabile_pct,
        ROUND(AVG(CASE WHEN voce = 'A2A' AND scadenza = 'A' THEN valore END), 2) AS tasso_imprese_pct,
        ROUND(AVG(CASE WHEN voce = 'L22' THEN valore END), 2) AS tasso_depositi_scadenza_pct
    FROM mir_raw
    WHERE tipo_dato = 'R' AND copertura_attivita = 'N'
      AND voce IN ('A2C', 'A2A', 'L22')
      AND trimestre IS NOT NULL
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
    c.cet1_pct,
    c.npl_ratio_pct,
    c.lcr_pct,
    -- Bilanci MFI (BSI)
    bsi.attivo_totale_mld,
    bsi.prestiti_mld,
    bsi.deposits_mld,
    bsi.obbligazioni_mld,
    bsi.capitale_mld,
    -- Tassi (MIR)
    mir.tasso_mutuo_pct,
    mir.tasso_imprese_pct,
    mir.tasso_depositi_scadenza_pct
FROM cbd2 c
LEFT JOIN bsi ON c.paese = bsi.paese AND c.anno = bsi.anno AND c.trimestre = bsi.trimestre
LEFT JOIN mir ON c.paese = mir.paese AND c.anno = mir.anno AND c.trimestre = mir.trimestre
ORDER BY c.paese, c.anno, c.trimestre
