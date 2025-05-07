-- opción 1: borrar toda la tabla de autores
DROP TABLE autores;
-- opción 2: borrar solo los docentes
DELETE FROM autores 
WHERE es_docente = TRUE

-- opción 3: borrar solo los alumnos
DELETE FROM autores 
WHERE es_docente = FALSE