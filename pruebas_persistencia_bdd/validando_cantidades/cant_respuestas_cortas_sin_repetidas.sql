-- cantidad de respuestas cortas no repetidas
-- 75
select count(distinct texto) as cant_respuestas_cortas from respuestas
where es_corta= TRUE