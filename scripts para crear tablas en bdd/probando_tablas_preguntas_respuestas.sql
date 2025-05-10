-- validaciones en la base de datos

------------------Preguntas -------------------------------------------------
/*
-- 484 mensajes que son identificados como preguntas
select count(*) as cant_mensajes_preguntas from mensajes
where es_pregunta=TRUE

-- 1793 cantidad de registros con contenido distinto
select count(distinct contenido) as cantidad_mensajes_distintos
from mensajes

-- 484 registros con texto diferente 
select count(distinct texto) as cant_preg_distintas
from preguntas

-- 484 registros en la tabla preguntas
select count(*) as cant_reg_preguntas
from preguntas
*/

----------------------- Respuestas ----------------------------------------------------

/*
-- 484 mensajes que son identificados como preguntas
select count(*) as cant_mensajes_preguntas from mensajes
where es_respuesta=TRUE

-- 1793 cantidad de registros con contenido distinto
select count(distinct contenido) as cantidad_mensajes_distintos
from mensajes

-- 484 registros con texto diferente 
select count(distinct texto) as cant_preg_distintas
from respuestas

-- 484 registros en la tabla preguntas
select count(*) as cant_reg_preguntas
from respuestas
*/


/*
select count(distinct texto)
from preguntas

select count(distinct texto)
from respuestas

SELECT p.pregunta_id, p.contenido
FROM preguntas p
LEFT JOIN respuestas r ON r.pregunta_id = p.id
WHERE r.id IS NULL;
*/