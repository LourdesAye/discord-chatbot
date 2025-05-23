-- Ver mensajes con 4 palabras o menos
/*
SELECT id_mensaje, contenido, fecha_mensaje
FROM mensajes
WHERE LENGTH(contenido) - LENGTH(REPLACE(contenido, ' ', '')) + 1 <=4
and es_pregunta = TRUE
*/

--TOOOODO esto? -> es una respuesta a la pregunta anterior de ese mismo autor
--está todo ok? -> es una respuesta a una pregunta anterior de ese mismo autor
--algo asi? -> era una respuesta de un hilo, de un autor distinto al que da origen a una pregunta 
--seria hacer eso no? -> es una respuesta a una pregunta anterior de ese mismo autor

SELECT id_mensaje, contenido, fecha_mensaje
FROM mensajes
WHERE LENGTH(contenido) - LENGTH(REPLACE(contenido, ' ', '')) + 1 <=5
and es_pregunta = TRUE

--TOOOODO esto? -> es una respuesta a la pregunta anterior de ese mismo autor
--está todo ok? -> es una respuesta a una pregunta anterior de ese mismo autor
--algo asi? -> era una respuesta de un hilo, de un autor distinto al que da origen a una pregunta 
--seria hacer eso no? -> es una nueva pregunta que el autor hace una vez que cierra su pregunta anterior (vuelve a repreguntar sobre el tema)
-- algo asi estaria mas acorde? -> es una nueva pregunta que el autor hace una vez que cierra su pregunta anterior (vuelve a repreguntar sobre el tema)

-- el resto de las preguntas son adminsitrativas
-- es igual que las tome en este caso sin contexto ya que no van a ser tenidas en cuenta para generar embeddings 

