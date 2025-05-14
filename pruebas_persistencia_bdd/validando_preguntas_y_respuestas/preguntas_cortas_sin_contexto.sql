SELECT id_pregunta, texto, sin_contexto
FROM preguntas
WHERE LENGTH(TRIM(texto)) - LENGTH(REPLACE(TRIM(texto), ' ', '')) + 1 <= 6;

-- Con longitud de 6 palabras
-- 5 de 7 preguntas, cuya longitud de palabras es de 6, no tendrían contexto.
-- 2 serían adminitsrativas

-- Con longitud de 7 palabras
-- 5 de 9 preguntas, cuya longitud de palabras es de 7, no tendrían contexto.
-- 3 serían administrativas y 1 hace referencia a una corrección
