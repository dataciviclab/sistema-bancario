-- mart_bsi_snapshot: Ultimo trimestre per paese
-- Pivot da clean_input (dati unpivoted)

WITH pivoted AS (
    SELECT
        paese, anno, trimestre,
        ROUND(AVG(CASE WHEN voce = 'T00' THEN valore / 1000 END), 1) AS attivo_totale_mld,
        ROUND(AVG(CASE WHEN voce = 'A20T' THEN valore / 1000 END), 1) AS prestiti_mld,
        ROUND(AVG(CASE WHEN voce = 'L20' THEN valore / 1000 END), 1) AS deposits_mld,
        ROUND(AVG(CASE WHEN voce = 'L40' THEN valore / 1000 END), 1) AS obbligazioni_mld,
        ROUND(AVG(CASE WHEN voce = 'L60' THEN valore / 1000 END), 1) AS capitale_mld,
        ROW_NUMBER() OVER (PARTITION BY paese ORDER BY anno DESC, trimestre DESC) AS rn
    FROM clean_input
    WHERE frequenza = 'Q' OR (frequenza = 'M' AND trimestre IS NOT NULL)
    AND voce IN ('T00', 'A20T', 'L20', 'L40', 'L60')
    GROUP BY paese, anno, trimestre
)
SELECT
    paese, anno, trimestre,
    attivo_totale_mld, prestiti_mld, deposits_mld,
    obbligazioni_mld, capitale_mld,
    ROUND(prestiti_mld / NULLIF(deposits_mld, 0) * 100, 1) AS rapporto_prestiti_deposits_pct,
    ROUND(prestiti_mld / NULLIF(attivo_totale_mld, 0) * 100, 1) AS prestiti_pct_attivo
FROM pivoted
WHERE rn = 1
ORDER BY paese
