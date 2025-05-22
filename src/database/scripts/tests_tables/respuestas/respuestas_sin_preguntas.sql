-- No se encontraron respuestas sin pregunta  
-- no devuelve filas
SELECT r.id_respuesta, r.texto, r.pregunta_id
FROM respuestas r LEFT JOIN  preguntas p
ON r.pregunta_id = p.id_pregunta
WHERE p.id_pregunta IS NULL;



