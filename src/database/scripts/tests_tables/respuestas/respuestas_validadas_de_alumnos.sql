SELECT r.id_respuesta, r.texto, a.nombre_autor, r.es_validada
FROM respuestas r
INNER JOIN mensajes m ON r.mensaje_id = m.id_mensaje
INNER JOIN autores a ON a.id_autor = m.autor_id
WHERE r.es_validada = TRUE AND a.es_docente = FALSE;