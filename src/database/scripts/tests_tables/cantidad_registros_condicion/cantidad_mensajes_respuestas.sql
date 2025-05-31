-- cantidad de registros en tabla MENSAJES, incluyendo repetidos, que son respuestas
-- 2020
select count(*) as cant_respuestas from mensajes m
where m.es_pregunta = FALSE