WITH mensajes_ordenados AS (
  SELECT 
    m.id_mensaje,
    m.contenido,
    m.autor_id,
    a.nombre_autor,
    a.es_docente,
    m.fecha_mensaje,
    m.es_pregunta,
    LEAD(m.id_mensaje) OVER (ORDER BY m.fecha_mensaje) AS siguiente_id,
    LEAD(m.contenido) OVER (ORDER BY m.fecha_mensaje) AS siguiente_contenido,
    LEAD(m.autor_id) OVER (ORDER BY m.fecha_mensaje) AS siguiente_autor_id
  FROM mensajes m
  JOIN autores a ON m.autor_id = a.id_autor
),
preguntas_y_respuestas_consecutivas AS (
  SELECT 
    m.id_mensaje AS pregunta_id,
    m.contenido AS pregunta_texto,
    m.autor_id,
    m.nombre_autor,
    m.siguiente_id AS respuesta_id,
    m.siguiente_contenido AS respuesta_texto
  FROM mensajes_ordenados m
  WHERE m.es_pregunta = TRUE
    AND m.es_docente = FALSE
    AND array_length(regexp_split_to_array(m.contenido, '\s+'), 1) <= 10
    AND m.autor_id = m.siguiente_autor_id
)
SELECT * FROM preguntas_y_respuestas_consecutivas;