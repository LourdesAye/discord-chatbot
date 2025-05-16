-- cantidad de registros en tabla MENSAJES sin repetidos que sean preguntas
-- 477
select count(distinct contenido) as cant_mensaj_pregu_dist from mensajes m
where es_pregunta = TRUE
