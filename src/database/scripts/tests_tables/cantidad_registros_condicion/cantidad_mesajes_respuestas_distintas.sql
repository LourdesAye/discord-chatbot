-- cantidad de registros en tabla MENSAJES sin repetidos que sean respuestas
-- 1249
select count(distinct contenido) as cant_mensaj_pregu_dist from mensajes m
--where es_pregunta = FALSE
where es_pregunta = FALSE