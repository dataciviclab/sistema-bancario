-- mart_bsi_snapshot: ultimo trimestre disponibile per paese
--
-- Snapshot per i confronti cross-country. Stesse serie dichiarate di
-- mart_bsi_balance, quindi stessi numeri: nessuna formula duplicata a mano.

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        MAX(CASE WHEN metrica = 'attivo_totale' THEN valore END) AS attivo_totale_mld,
        MAX(CASE WHEN metrica = 'prestiti' THEN valore END) AS prestiti_mld,
        MAX(CASE WHEN metrica = 'depositi' THEN valore END) AS depositi_mld,
        MAX(CASE WHEN metrica = 'obbligazioni' THEN valore END) AS obbligazioni_mld,
        MAX(CASE WHEN metrica = 'capitale_riserve' THEN valore END) AS capitale_mld
    FROM clean_input
    WHERE trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F')
    GROUP BY paese, anno, trimestre
),

ultimo AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY paese ORDER BY anno DESC, trimestre DESC) AS rn
    FROM serie
    WHERE attivo_totale_mld IS NOT NULL
)

SELECT
    paese,
    anno,
    trimestre,
    ROUND(attivo_totale_mld, 1) AS attivo_totale_mld,
    ROUND(prestiti_mld, 1) AS prestiti_mld,
    ROUND(depositi_mld, 1) AS depositi_mld,
    ROUND(obbligazioni_mld, 1) AS obbligazioni_mld,
    ROUND(capitale_mld, 1) AS capitale_mld,
    ROUND(prestiti_mld / NULLIF(depositi_mld, 0) * 100, 1) AS rapporto_prestiti_deposits_pct,
    ROUND(prestiti_mld / NULLIF(attivo_totale_mld, 0) * 100, 1) AS prestiti_pct_attivo
FROM ultimo
WHERE rn = 1
ORDER BY paese
