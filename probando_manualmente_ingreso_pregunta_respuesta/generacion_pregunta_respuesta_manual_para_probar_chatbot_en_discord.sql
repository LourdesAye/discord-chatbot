-- 1 generación de mensaje
-- gonza3843
--insert into mensajes (id_mensaje_discord,autor_id,fecha_mensaje,contenido,es_pregunta,origen)
--values (12345678910111213,9,TO_DATE('2025-10-21','YYYY-MM-DD'), 'mi duda es sobre qué es git',TRUE,'prueba_manual');

-- 2 buscar el mensaje insertado para obtener id_mensaje propio necesario para pregunta por fk
-- select * from mensajes where origen='prueba_manual'
-- id_mensaje 9994

-- 3 generacion de pregunta
-- insert into preguntas (mensaje_id,texto,esta_cerrada,sin_contexto,es_administrativa)
-- values (9994,'mi duda es sobre qué es git',TRUE,FALSE,FALSE)

-- 4 buscar la pregunta insertada para obtener id_pregunta propia necesario para respuesta por fk
-- select * from preguntas where texto='mi duda es sobre qué es git'
-- id_pregunta : 1917

-- 5 para una respuesta necesito que sea primero mensaje y luego respuesta con pregunta como pk
-- 10 : felipe.3838
-- insert into mensajes (id_mensaje_discord,autor_id,fecha_mensaje,contenido,es_pregunta,origen)
-- values (345678910111213,10,TO_DATE('2025-10-22','AAAA-MM-DD'),'Es para versionado de un proyecto, en tu pc podes tener varias versiones de tu proyecto e ir cambiando entre ellas',FALSE,'prueba_manual')

-- 6 buscar mensaje porque necesito su id para generar la respuesta
-- select * from mensajes 
-- where contenido='Es para versionado de un proyecto, en tu pc podes tener varias versiones de tu proyecto e ir cambiando entre ellas'
-- id_mensaje 9995

-- 7 generar respuesta
-- insert into respuestas(mensaje_id,pregunta_id,texto,orden,es_validada,es_corta)
-- values (9995,1917,'Es para versionado de un proyecto, en tu pc podes tener varias versiones de tu proyecto e ir cambiando entre ellas',1,FALSE,FALSE)

-- 8 ver respuesta en la tabla
-- select * from respuestas where texto ='Es para versionado de un proyecto, en tu pc podes tener varias versiones de tu proyecto e ir cambiando entre ellas'
-- 8077

-- 9 me equivoque y no hay preguntas esta_cerrada en false
-- hice esta consulta y me dio esta_cerrada = true
--select * from preguntas
--where id_pregunta=1917

-- 10 actualizo pregunta como esta_cerrada en false
-- UPDATE preguntas SET esta_cerrada=FALSE WHERE id_pregunta=1917;

-- 11 vuelvo a consultar
-- select * from preguntas
-- where id_pregunta=1917

-- 12 me quedo mal fecha de mensaje de la respuesta
-- select * from respuestas 
-- where pregunta_id = 1917

-- 13 pero la fecha esta en mensaje
-- select * from mensajes
-- where id_mensaje = 9995

-- 14 actualizo fecha
--UPDATE mensajes SET fecha_mensaje= TO_DATE('2025-10-21 05:10:20','AAAA-MM-DD HH:MM:SS')
--WHERE id_mensaje=9995

-- 15 viendo si actualizo mensaje
--select * from mensajes
-- where id_mensaje = 9995

-- 16 no actualizo investigacion en chatgpt de por qué no funciona tal cual como lo puse
/*
PROBLEMAS:
1- TO_DATE() devuelve solo una fecha sin hora, convierte a DATE, no a TIMESTAMP. 
2- El formato 'AAAA-MM-DD HH:MM:SS' no es válido en PostgreSQL (usa 'YYYY-MM-DD HH24:MI:SS').  
3- Como el campo fecha_mensaje es tipo TIMESTAMP, PostgreSQL hace una conversión implícita errónea 
desde una fecha sin hora (por eso te aparece 0001-10-21 00:00:00 BC).

SOLUCIONES: 
1- Usar TO_TIMESTAMP (no TO_DATE) y el formato correcto:
UPDATE mensajes
SET fecha_mensaje = TO_TIMESTAMP('2025-10-21 05:10:20', 'YYYY-MM-DD HH24:MI:SS')
WHERE id_mensaje = 9995;

2- evitar el formato y usar directamente un literal de timestamp
UPDATE mensajes
SET fecha_mensaje = '2025-10-21 05:10:20'::timestamp
WHERE id_mensaje = 9995;
*/

-- Probando solución
/*
UPDATE mensajes
SET fecha_mensaje = TO_TIMESTAMP('2025-10-21 05:10:20', 'YYYY-MM-DD HH24:MI:SS')
WHERE id_mensaje = 9995;
*/

-- Verificando el cambio
--SELECT *
--FROM mensajes
--WHERE id_mensaje = 9995;

-- ahora si primer lote manual de mensaje- pregunta y mensaje - respuesta ya persistidos 
-- en base de datos relacional
-- para probar funcionalidad de traer preguntas abiertas desde la base de datos necesarios para
-- el chatbot en discord, para mensajes en tiempo real








