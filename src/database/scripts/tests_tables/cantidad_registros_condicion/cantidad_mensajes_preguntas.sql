-- cantidad de registros en tabla MENSAJES, incluyendo repetidos, que son preguntas
-- 479
select count(*) as cant_respuestas from mensajes m
where m.es_pregunta = TRUE