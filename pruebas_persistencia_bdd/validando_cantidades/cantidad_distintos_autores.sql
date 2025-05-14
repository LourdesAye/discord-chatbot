-- cantidad de registros en la tabla autores sin repetidos
-- 153
select count(distinct nombre_autor) as cant_autores_dist from autores