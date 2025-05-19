-- Preguntas sin ninguna respuesta validada
-- 17 registros
/*
SELECT p.id_pregunta, p.texto
FROM preguntas p
WHERE p.id_pregunta NOT IN (
    SELECT r.pregunta_id
    FROM respuestas r
    WHERE r.es_validada = TRUE
);
*/

SELECT p.id_pregunta, p.texto
FROM preguntas p
LEFT JOIN (
    SELECT DISTINCT r.pregunta_id
    FROM respuestas r
    WHERE r.es_validada = TRUE
) AS r_valid ON p.id_pregunta = r_valid.pregunta_id
WHERE r_valid.pregunta_id IS NULL;