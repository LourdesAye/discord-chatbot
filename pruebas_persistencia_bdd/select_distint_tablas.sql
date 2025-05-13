-- dio 486 
-- select distinct  count(texto) from preguntas -- cuidado aca esto es: Esta consulta intenta contar los valores 
-- en contenido, pero luego aplica DISTINCT al resultado del COUNT(contenido).
-- Lo que sucede aquí es que COUNT(contenido) siempre devuelve un único número 
-- (el total de filas donde contenido no es NULL).
-- DISTINCT en este caso no tiene sentido porque COUNT(contenido) ya es un solo valor, por lo que esta consulta 
-- probablemente devuelva solo una fila con ese número.

-- dio 2035
-- select count(*) from respuestas
-- select * from mensajes


--SELECT COUNT(DISTINCT contenido) AS cantidad_contenidos_distintos
--FROM mensajes; -- 1793

-- SELECT COUNT(DISTINCT texto) AS cantidad_contenidos_distintos
-- FROM preguntas; -- 486

--SELECT COUNT(DISTINCT texto) AS cantidad_contenidos_distintos
--FROM respuestas; -- 1307

-- cuáles son los contenidos repetidos y cuántas veces aparecen
-- SELECT contenido, COUNT(*) as cantidad
-- FROM mensajes
-- GROUP BY contenido
-- HAVING COUNT(*) > 1
-- ORDER BY cantidad DESC;

