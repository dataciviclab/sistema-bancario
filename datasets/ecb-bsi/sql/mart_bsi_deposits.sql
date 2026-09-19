-- mart_bsi_deposits: Composizione depositi per paese/trimestre

SELECT
    paese,
    anno,
    trimestre,
    -- Depositi (miliardi EUR, media trimestrale)
    ROUND(AVG(CASE WHEN voce = 'L20' THEN valore / 1000 END), 1) AS deposits_totali_mld,
    ROUND(AVG(CASE WHEN voce = 'L21' THEN valore / 1000 END), 1) AS deposits_overnight_mld,
    ROUND(AVG(CASE WHEN voce = 'L22' THEN valore / 1000 END), 1) AS deposits_a_scadenza_mld,
    ROUND(AVG(CASE WHEN voce = 'L23' THEN valore / 1000 END), 1) AS deposits_preavviso_mld,
    -- Composizione
    ROUND(
        AVG(CASE WHEN voce = 'L21' THEN valore END) /
        NULLIF(AVG(CASE WHEN voce = 'L20' THEN valore END), 0) * 100
    , 1) AS pct_overnight,
    ROUND(
        AVG(CASE WHEN voce = 'L22' THEN valore END) /
        NULLIF(AVG(CASE WHEN voce = 'L20' THEN valore END), 0) * 100
    , 1) AS pct_scadenza,
    ROUND(
        AVG(CASE WHEN voce = 'L23' THEN valore END) /
        NULLIF(AVG(CASE WHEN voce = 'L20' THEN valore END), 0) * 100
    , 1) AS pct_preavviso
FROM clean_input
WHERE frequenza = 'Q' OR (frequenza = 'M' AND trimestre IS NOT NULL)
GROUP BY paese, anno, trimestre
ORDER BY paese, anno, trimestre
