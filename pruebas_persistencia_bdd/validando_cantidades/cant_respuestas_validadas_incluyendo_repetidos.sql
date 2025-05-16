-- cantidad de respuestas validadas
-- 1165
select count(*) as cant_respuestas_validadas from respuestas
where es_validada= TRUE