-- mart_mir_volumi: quanto credito nuovo ogni trimestre
--
-- ATTENZIONE alla differenza con mart_mir_rates: qui i valori sono FLUSSI
-- mensili (nuovi contratti del mese), quindi nel trimestre si SOMMANO. I tassi
-- sono livelli, quindi si MEDIANO. Confondere le due cose produce numeri
-- sbagliati di un fattore 3.
--
-- Per le imprese la BCE non pubblica un totale "tutti gli importi" completo:
-- il totale e' fino a 1 mln + oltre 1 mln.

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        SUM(CASE WHEN metrica = 'volume_mutui' THEN valore END) AS volume_mutui_mld,
        SUM(CASE WHEN metrica = 'volume_consumo' THEN valore END) AS volume_consumo_mld,
        SUM(CASE WHEN metrica = 'volume_prestiti_piccole' THEN valore END) AS volume_prestiti_piccole_mld,
        SUM(CASE WHEN metrica = 'volume_prestiti_grandi' THEN valore END) AS volume_prestiti_grandi_mld,
        COUNT(DISTINCT CASE WHEN metrica = 'volume_mutui' THEN periodo END) AS mesi_mutui
    FROM clean_input
    WHERE trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F')
      AND metrica LIKE 'volume_%'
    GROUP BY paese, anno, trimestre
)

SELECT
    paese,
    anno,
    trimestre,
    ROUND(volume_mutui_mld, 1) AS volume_mutui_mld,
    ROUND(volume_consumo_mld, 1) AS volume_consumo_mld,
    ROUND(volume_prestiti_piccole_mld, 1) AS volume_prestiti_piccole_mld,
    ROUND(volume_prestiti_grandi_mld, 1) AS volume_prestiti_grandi_mld,
    ROUND(COALESCE(volume_prestiti_piccole_mld, 0) + COALESCE(volume_prestiti_grandi_mld, 0), 1)
        AS volume_prestiti_imprese_mld,
    -- Quota di credito nuovo alle imprese che va alle piccole
    ROUND(volume_prestiti_piccole_mld
          / NULLIF(volume_prestiti_piccole_mld + volume_prestiti_grandi_mld, 0) * 100, 1)
        AS quota_piccole_imprese_pct,
    mesi_mutui
FROM serie
WHERE volume_mutui_mld IS NOT NULL OR volume_prestiti_piccole_mld IS NOT NULL
ORDER BY paese, anno, trimestre
