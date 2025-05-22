-- cantidad de respuestas validadas no repetidas
-- 706
select count(distinct texto) as cant_respuestas_validadas from respuestas
where es_validada= TRUE