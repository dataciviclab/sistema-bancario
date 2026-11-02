-- mart_bsi_crediti: a chi prestano le banche, per settore
--
-- Una riga = paese x trimestre. Stock di prestiti a famiglie e a societa' non
-- finanziarie, a fine trimestre.
--
-- ATTENZIONE alla regola di aggregazione: i prestiti sono STOCK. La sorgente
-- e' mensile, quindi nel trimestre si prende l'ultimo mese disponibile, non la
-- media (come i tassi) ne' la somma (come i volumi). Tre regole diverse per tre
-- fenomeni diversi, dichiarate nei rispettivi mart.

WITH mensile AS (
    SELECT
        paese,
        anno,
        trimestre,
        periodo,
        metrica,
        valore,
        ROW_NUMBER() OVER (
            PARTITION BY paese, anno, trimestre, metrica ORDER BY periodo DESC
        ) AS rn
    FROM clean_input
    WHERE metrica IN ('prestiti_famiglie', 'prestiti_imprese')
      AND trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F')
),

fine_periodo AS (
    SELECT
        paese,
        anno,
        trimestre,
        MAX(CASE WHEN metrica = 'prestiti_famiglie' THEN valore END) AS prestiti_famiglie_mld,
        MAX(CASE WHEN metrica = 'prestiti_imprese' THEN valore END) AS prestiti_imprese_mld,
        MAX(periodo) AS mese_riferimento
    FROM mensile
    WHERE rn = 1
    GROUP BY paese, anno, trimestre
)

SELECT
    paese,
    anno,
    trimestre,
    mese_riferimento,
    ROUND(prestiti_famiglie_mld, 1) AS prestiti_famiglie_mld,
    ROUND(prestiti_imprese_mld, 1) AS prestiti_imprese_mld,
    ROUND(COALESCE(prestiti_famiglie_mld, 0) + COALESCE(prestiti_imprese_mld, 0), 1)
        AS prestiti_famiglie_imprese_mld,
    ROUND(prestiti_famiglie_mld
          / NULLIF(prestiti_famiglie_mld + prestiti_imprese_mld, 0) * 100, 1)
        AS quota_famiglie_pct
FROM fine_periodo
WHERE prestiti_famiglie_mld IS NOT NULL OR prestiti_imprese_mld IS NOT NULL
ORDER BY paese, anno, trimestre
