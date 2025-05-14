-- probando valor de las preguntas cortas
SELECT *
FROM respuestas
WHERE LENGTH(TRIM(texto)) <= 14;  -- limite de caracteres en el texto
-- 126 respuestas con 14 caracteres no aportan valor
--where es_corta=TRUE

--SELECT *
--FROM respuestas
--WHERE array_length(regexp_split_to_array(trim(texto), '\s+'), 1) <= 1; -- o el número de palabras
-- siempre se filtra alguna respuesta como enlace

