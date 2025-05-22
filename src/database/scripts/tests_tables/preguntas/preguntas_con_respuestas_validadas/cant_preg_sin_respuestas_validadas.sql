-- Cantidad de preguntas sin respuestas validadas
-- 0
SELECT COUNT(*) AS cantidad_preguntas_sin_respuesta_validada
FROM preguntas p
WHERE p.id_pregunta NOT IN (
    SELECT id_pregunta
    FROM respuestas
    WHERE es_validada = TRUE
);