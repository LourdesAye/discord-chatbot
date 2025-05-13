----------------------------------------------- Mensajes -------------------------------------------------
/*
-- 1794 cantidad de registros con contenido distinto en tabla mensajes
select count(distinct contenido) as cantidad_mensajes_distintos
from mensajes


-- 2512 cantidad de registros en tabla mensajes (todos, incluye repetidos)
select count(*) as cantidad_mensajes_distintos
from mensajes
*/
---------------------------------------------- Preguntas -------------------------------------------------
/*
-- 489 mensajes que son identificados como preguntas en tabla mensajes
select count(*) as cant_mensajes_preguntas from mensajes
where es_pregunta=TRUE

-- 489 registros con texto diferente en tabla pregunta
select count(distinct texto) as cant_preg_distintas
from preguntas

-- 489 registros en la tabla preguntas
select count(*) as cant_reg_preguntas
from preguntas
*/

----------------------------------------------- Respuestas ------------------------------------------------------
/*
-- 2023 mensajes que son identificados como respuestas
select count(*) as cant_mensajes_respuestas from mensajes
where es_respuesta=TRUE

-- 1305 registros de tabla respuestas con texto diferente 
select count(distinct texto) as cant_respuestas_distintas
from respuestas

-- 2023 registros en la tabla preguntas
select count(*) as cant_reg_preguntas
from respuestas
*/


-- se identificaron 3 preguntas sin respuestas
SELECT p.id_pregunta, p.texto, r.id_respuesta
FROM preguntas p LEFT JOIN respuestas r 
ON r.pregunta_id = p.id_pregunta
WHERE r.pregunta_id IS NULL;


--------------------ACA CAMBIOS EN PREGUNTAS Y JUSTIFICACION ----------------------------------

----------------------- ANÁLISIS : Preguntas sin respuestas ---------------------------------------
/*
-- preguntas sin respuestas = 3 : no deberian cargarse , validar desde python y agregar en un log
SELECT p.id_pregunta, p.texto, r.id_respuesta
FROM preguntas p LEFT JOIN respuestas r 
ON r.pregunta_id = p.id_pregunta
WHERE r.pregunta_id IS NULL;

-- revisada :
id_pregunta: 95, texto : "Hola Buenaas, como va?
Estuve haciendo el final de equiapp y en el modelado de datos que hicimos en clase tiene claves cmopuestas.
Mi pregunta seria, cuando deberiamos usar ese tipo de calves sobre PK normales gracias "
NO TUVO RESPUESTA EFECTIVAMENTE

id_pregunta: 303 texto: Si alguien sabe dónde están 🥲 Genia, gracias 
(pregunta de un mismo autor segmentada, pero antes habia dado cierre de su conuslta, no aporta)

id_pregunta: 383 texto: Disculpen, queria hacer una consulta con respecto al rol de discord. Soy del grupo 25 y solo se me habilitó el chat de voz mientras que mis compañeros tienen ambos desde ya muchas gracias 🙂
(es pregunta administrativa, tambien habia dado un mensaje de corte previa)
*/


/*
-- ANÁLISIS : Respuestas sin pregunta asociada (no deberían existir) 
-- ninguna respuesta sin pregunta -- EXCELENTE
SELECT r.id_respuesta, r.texto
FROM respuestas r LEFT JOIN preguntas p 
ON r.pregunta_id = p.id_pregunta
WHERE p.id_pregunta IS NULL;
*/

/*
-- POR CADA PREGUNTA SE CALCULA LA CANTIDAD DE RESPUESTAS
-- Preguntas con muchas respuestas (¿esperado o excesivo?)
-- Preguntas con 10+ respuestas podrían ser chequeadas manualmente para ver si no se unificó mal.
SELECT p.id_pregunta, p.texto, COUNT(r.id_respuesta) as cantidad_respuestas
FROM preguntas p
LEFT JOIN respuestas r ON r.pregunta_id = p.id_pregunta
GROUP BY p.id_pregunta
ORDER BY cantidad_respuestas DESC;
*/

/* ANALIZANDO UNA PREGUNTA 8: 
SELECT r.id_respuesta, r.texto, p.id_pregunta, p.texto
FROM preguntas p LEFT JOIN respuestas r 
ON r.pregunta_id = p.id_pregunta
WHERE r.pregunta_id = 8;
*/

--select * from  respuestas

/* para validar coherencia de tiempo, que sean cercanas en el tiempo las respuestas

SELECT * FROM respuestas r
WHERE r.pregunta_id = 8 
inner join mensajes m
ON m.id_mensaje = r.mensaje_id 
ORDER BY fecha_mensaje;
*/

-- Te da todas las respuestas asociadas a la pregunta 8.
-- Muestra la fecha de cada mensaje (respuesta).
-- Las ordena cronológicamente.
/*
SELECT r.*, m.fecha_mensaje, p.texto
FROM respuestas r
INNER JOIN mensajes m ON m.id_mensaje = r.mensaje_id
INNER JOIN preguntas p on p.id_pregunta = r.pregunta_id
WHERE r.pregunta_id = 208
ORDER BY m.fecha_mensaje;
*/


