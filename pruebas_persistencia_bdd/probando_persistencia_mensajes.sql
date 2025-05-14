-- cantidad total de registros en tabla mensaje: 2521
select count(*) from mensajes

-- cantidad total de mensajes que son respuestas: 2035
select count(*) from mensajes
where es_pregunta = FALSE

-- cantidad de mensajes que son preguntas: 486
select count(*) from mensajes
where es_pregunta = TRUE

-- cantidad total de mensajes que son no son respuestas: 486
select count(*) from mensajes
where es_pregunta = TRUE

-- cantidad total de mensajes que son no son pregunta: 2035
select count(*) from mensajes
where es_pregunta = FALSE
