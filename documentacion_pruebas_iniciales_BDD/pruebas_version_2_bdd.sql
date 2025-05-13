-- cantidad de registros de la tabla mensajes : 2521
-- select count(*) from mensajes
-- cantidad de mensajes que tienen contenido distinto: 1793
-- select count(distinct contenido) from mensajes

-- cantidad de registros de la tabla respuestas: 2035
-- select count(*) from respuestas
-- cantidad de registros de la tabla preguntas: 486
-- select count(*) from preguntas

-- cantidad de peguntas que tienen texto distinto : 486
-- select count(distinct texto) from preguntas

-- cantidad de respuestas que tienen texto distinto : 1307
-- select count (distinct texto) from respuestas

-- probando si preguntas de alumnos fragmentadas en varios mensajes se unifican en una única pregunta
-- SELECT * FROM preguntas
-- WHERE texto LIKE '%Buenas! Consulta, que aula tenemos hoy? %';

-- SELECT * FROM preguntas
-- WHERE texto LIKE '%Hola Buenas una consulta %';

select * from adjuntos
