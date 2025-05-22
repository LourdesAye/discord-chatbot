-- cantidad de preguntas sin contexto no repetidas
-- 8
select count(distinct texto) as cant_preguntas_sin_contexto from preguntas
where sin_contexto= TRUE