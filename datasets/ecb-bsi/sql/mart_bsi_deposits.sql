-- mart_bsi_deposits: chi tiene i depositi
--
-- La vecchia versione divideva i depositi per scadenza (conti correnti, a
-- scadenza, preavviso) prendendo la media di serie mensili con decine di
-- controparti diverse: numeri non verificabili. La BCE non pubblica quel
-- totale trimestrale come serie unica; pubblica invece la scomposizione per
-- detentore, che qui e' dichiarata serie per serie.

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        MAX(CASE WHEN metrica = 'depositi' THEN valore END) AS depositi_totali_mld,
        MAX(CASE WHEN metrica = 'depositi_famiglie_imprese' THEN valore END) AS depositi_famiglie_imprese_mld,
        MAX(CASE WHEN metrica = 'depositi_banche' THEN valore END) AS depositi_banche_mld,
        MAX(CASE WHEN metrica = 'depositi_governo_centrale' THEN valore END) AS depositi_governo_centrale_mld
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
    ROUND(depositi_totali_mld, 1) AS depositi_totali_mld,
    ROUND(depositi_famiglie_imprese_mld, 1) AS depositi_famiglie_imprese_mld,
    ROUND(depositi_banche_mld, 1) AS depositi_banche_mld,
    ROUND(depositi_governo_centrale_mld, 1) AS depositi_governo_centrale_mld,
    ROUND(depositi_famiglie_imprese_mld / NULLIF(depositi_totali_mld, 0) * 100, 1) AS pct_famiglie_imprese,
    ROUND(depositi_banche_mld / NULLIF(depositi_totali_mld, 0) * 100, 1) AS pct_banche
FROM serie
WHERE depositi_totali_mld IS NOT NULL
ORDER BY paese, anno, trimestre
