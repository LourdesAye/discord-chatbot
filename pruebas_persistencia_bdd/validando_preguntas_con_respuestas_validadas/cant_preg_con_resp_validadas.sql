-- Cantidad de preguntas con al menos una respuesta validada
--460
SELECT COUNT(DISTINCT p.id_pregunta) AS cantidad_preguntas_con_respuesta_validada
FROM preguntas p
JOIN respuestas r ON p.id_pregunta = r.pregunta_id
WHERE r.es_validada = TRUE;