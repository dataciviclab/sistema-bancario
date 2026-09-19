-- mart_panorama: Vista unificata tutti i KPI per paese/trimestre

SELECT
    paese,
    anno,
    trimestre,
    -- Profittabilita
    roe_pct,
    roa_pct,
    costo_reddito_pct,
    -- Capitale
    cet1_pct,
    -- Qualita credito
    npl_ratio_pct,
    -- Liquidita
    lcr_pct,
    -- Bilanci
    attivo_totale_mld,
    prestiti_mld,
    deposits_mld,
    -- Tassi
    tasso_mutuo_pct,
    tasso_imprese_pct,
    tasso_depositi_scadenza_pct
FROM clean_input
ORDER BY paese, anno, trimestre
