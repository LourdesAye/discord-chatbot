-- Ver mensajes con 4 palabras o menos
SELECT id_mensaje, contenido, fecha_mensaje
FROM mensajes
WHERE LENGTH(contenido) - LENGTH(REPLACE(contenido, ' ', '')) + 1 <=4
and es_pregunta = TRUE


--TOOOODO esto? -> es una respuesta a la pregunta anterior de ese mismo autor
--está todo ok? -> es una respuesta a una pregunta anterior de ese mismo autor
--algo asi? -> 245 -> era una respuesta de un hilo, de un autor distinto al que da origen a una pregunta- 
--Algo asi estaria mas acorde? -> 551 ->es una respuesta a una pregunta anterior de ese mismo autor
--seria hacer eso no? ->  1804 -> es una respuesta a una pregunta anterior de ese mismo autor

-- como son casos puntuales es conveniente una vez que se cierren todas las preguntas, tendria que agregar esta pregunta como respuesta y las respuestas que le siguen


