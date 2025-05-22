-- preguntas con al menos una respuesta validada
-- 460
SELECT DISTINCT p.id_pregunta, p.texto
FROM preguntas p
JOIN respuestas r ON p.id_pregunta = r.pregunta_id
WHERE r.es_validada = TRUE;