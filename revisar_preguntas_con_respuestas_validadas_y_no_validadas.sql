SELECT DISTINCT p.id_pregunta, p.texto
FROM preguntas p
JOIN respuestas r ON r.pregunta_id = p.id_pregunta
WHERE 
--r.es_validada = true
  --AND 
  (p.sin_contexto = false)
  AND (p.es_administrativa = false)

