-- preguntas administrativas o sin contexto
select count(*) as cant_preg_adm_y_sin_contexto from preguntas
where es_administrativa = true
or sin_contexto = true