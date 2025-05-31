-- preguntas administrativas o sin contexto
select * from preguntas
where es_administrativa = true
or sin_contexto = true