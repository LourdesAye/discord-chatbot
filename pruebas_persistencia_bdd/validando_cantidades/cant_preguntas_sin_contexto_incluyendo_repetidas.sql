-- cantidad de preguntas sin contexto con repetidas
-- 8
select count(texto) as cant_preguntas_sin_contexto from preguntas
where sin_contexto= TRUE