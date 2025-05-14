-- No se encontraron preguntas sin respuestas  
-- no devuelve filas
SELECT p.id_pregunta, p.texto, r.id_respuesta
FROM preguntas p LEFT JOIN respuestas r 
ON r.pregunta_id = p.id_pregunta
WHERE r.pregunta_id IS NULL;



