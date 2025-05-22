select 
p.id_pregunta,p.texto,p.sin_contexto,p.es_administrativa,a1.nombre_autor,
m.fecha_mensaje,
r.id_respuesta, r.texto,r.es_validada,r.es_corta,a2.nombre_autor
from preguntas p
INNER JOIN mensajes m ON p.mensaje_id = m.id_mensaje
INNER JOIN autores a1 ON m.autor_id = a1.id_autor
INNER JOIN respuestas r ON r.pregunta_id = p.id_pregunta
INNER JOIN mensajes m2 ON r.mensaje_id = m2.id_mensaje
INNER JOIN autores a2 ON m2.autor_id = a2.id_autor;