-- mart_bls_credit: Condizioni di credito per paese/trimestre
-- Filtra: solo indicatori chiave (credit standards, loan demand)
-- Valori: diffusion index (positivo = peggioramento, negativo = miglioramento)

SELECT
    paese,
    anno,
    trimestre,
    -- Credit standards imprese (net change)
    AVG(CASE WHEN voce = 'BC' THEN valore END) AS cs_imprese,
    -- Credit standards PMI
    AVG(CASE WHEN voce = 'SME' THEN valore END) AS cs_pmi,
    -- Credit standards grandi imprese
    AVG(CASE WHEN voce = 'LE' THEN valore END) AS cs_grandi,
    -- Margins on loans
    AVG(CASE WHEN voce = 'MAL' THEN valore END) AS margins_prestiti,
    -- Non-interest charges
    AVG(CASE WHEN voce = 'NIC' THEN valore END) AS spese_non_interesse,
    -- Loan demand imprese
    AVG(CASE WHEN voce = 'LP' THEN valore END) AS domanda_credito_imprese,
    -- Loan demand households
    AVG(CASE WHEN voce = 'CP' THEN valore END) AS domanda_credito_famiglie
FROM clean_input
WHERE trimestre IS NOT NULL
  AND voce IN ('BC', 'SME', 'LE', 'MAL', 'NIC', 'LP', 'CP')
GROUP BY paese, anno, trimestre
ORDER BY paese, anno, trimestre
