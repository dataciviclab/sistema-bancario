-- mart_bsi_balance: Bilanci MFI per paese/trimestre
-- Aggrega a livello trimestrale (media dei 3 mesi)

SELECT
    paese,
    anno,
    trimestre,
    -- Voci di bilancio (miliardi EUR, media trimestrale)
    ROUND(AVG(CASE WHEN voce = 'T00' THEN valore / 1000 END), 1) AS attivo_totale_mld,
    ROUND(AVG(CASE WHEN voce = 'A20T' THEN valore / 1000 END), 1) AS prestiti_mld,
    ROUND(AVG(CASE WHEN voce = 'L20' THEN valore / 1000 END), 1) AS deposits_mld,
    ROUND(AVG(CASE WHEN voce = 'L40' THEN valore / 1000 END), 1) AS obbligazioni_mld,
    ROUND(AVG(CASE WHEN voce = 'L60' THEN valore / 1000 END), 1) AS capitale_mld,
    -- Ratio
    ROUND(
        AVG(CASE WHEN voce = 'A20T' THEN valore END) /
        NULLIF(AVG(CASE WHEN voce = 'L20' THEN valore END), 0) * 100
    , 1) AS rapporto_prestiti_deposits_pct,
    ROUND(
        AVG(CASE WHEN voce = 'A20T' THEN valore END) /
        NULLIF(AVG(CASE WHEN voce = 'T00' THEN valore END), 0) * 100
    , 1) AS prestiti_pct_attivo
FROM clean_input
WHERE frequenza = 'Q' OR (frequenza = 'M' AND trimestre IS NOT NULL)
GROUP BY paese, anno, trimestre
ORDER BY paese, anno, trimestre
