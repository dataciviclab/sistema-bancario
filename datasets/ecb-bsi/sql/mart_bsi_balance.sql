-- mart_bsi_balance: bilanci MFI per paese/trimestre
--
-- Una colonna = una serie dichiarata in series_catalog.csv. Nessun AVG su
-- dimensioni eterogenee: ogni MAX(CASE ...) seleziona una serie sola.
-- Gli aggregati BCE (4F, U2, U5) restano fuori dal campo `paese`.

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        MAX(CASE WHEN metrica = 'attivo_totale' THEN valore END) AS attivo_totale_mld,
        MAX(CASE WHEN metrica = 'prestiti' THEN valore END) AS prestiti_mld,
        MAX(CASE WHEN metrica = 'prestiti_famiglie_imprese' THEN valore END) AS prestiti_famiglie_imprese_mld,
        MAX(CASE WHEN metrica = 'depositi' THEN valore END) AS depositi_mld,
        MAX(CASE WHEN metrica = 'depositi_famiglie_imprese' THEN valore END) AS depositi_famiglie_imprese_mld,
        MAX(CASE WHEN metrica = 'obbligazioni' THEN valore END) AS obbligazioni_mld,
        MAX(CASE WHEN metrica = 'capitale_riserve' THEN valore END) AS capitale_mld
    FROM clean_input
    WHERE trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F')
    GROUP BY paese, anno, trimestre
)

SELECT
    paese,
    anno,
    trimestre,
    ROUND(attivo_totale_mld, 1) AS attivo_totale_mld,
    ROUND(prestiti_mld, 1) AS prestiti_mld,
    ROUND(prestiti_famiglie_imprese_mld, 1) AS prestiti_famiglie_imprese_mld,
    ROUND(depositi_mld, 1) AS depositi_mld,
    ROUND(depositi_famiglie_imprese_mld, 1) AS depositi_famiglie_imprese_mld,
    ROUND(obbligazioni_mld, 1) AS obbligazioni_mld,
    ROUND(capitale_mld, 1) AS capitale_mld,
    -- Stesso perimetro (banche, residenti area euro) a numeratore e denominatore
    ROUND(prestiti_mld / NULLIF(depositi_mld, 0) * 100, 1) AS rapporto_prestiti_deposits_pct,
    ROUND(prestiti_mld / NULLIF(attivo_totale_mld, 0) * 100, 1) AS prestiti_pct_attivo
FROM serie
-- Solo trimestri completi: le serie B (deposit-taking corporations) partono nel
-- 2006-2008 per alcuni paesi, le A nel 2003. Una riga con bilancio parziale
-- sarebbe una lettura sbagliata, non un dato mancante.
WHERE attivo_totale_mld IS NOT NULL
  AND prestiti_mld IS NOT NULL
  AND depositi_mld IS NOT NULL
ORDER BY paese, anno, trimestre
