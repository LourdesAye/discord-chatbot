-- cantidad de preguntas administrativas con repetidas
-- 116
select count(texto) as cant_preguntas_administrativas from preguntas
where es_administrativa= TRUE