-- cantidad de registros en tabla MENSAJES sin repetidos
-- 1729
select count(distinct contenido) as cant_mensaj_dist from mensajes m