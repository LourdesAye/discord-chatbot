-- cantidad de registros en tabla MENSAJES sin repetidos
-- 1731
select count(distinct contenido) as cant_mensaj_dist from mensajes m