-- cantidad de preguntas administrativas no repetidas
-- 116
select count(distinct texto) as cant_preguntas_administrativas from preguntas
where es_administrativa= TRUE