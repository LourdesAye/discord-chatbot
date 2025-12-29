from abc import ABC, abstractmethod # para crear clase abstracta y obligar a definir métodos a las clases hijas
from database.database.models.clase_mensajes import Mensaje
from database.database.models.clase_preguntas import Pregunta
from utils.utilidades_logs import setup_logger
from database.database.models.clase_autores import lista_docentes
from database.database.services.procesamiento_batch import ProcesadorBatch

# tengo dudas si agregar id de preguntas o respuestas en tiempo real cuando se cargan d ela base de datos y tambien cuando se ponene en logs
# tal vez deba porque los logs permiten el seguimiento de cada pregunta o respuesta, daria trazabilidad

logger_msj = setup_logger('procesamiento_de_mensajes', 'logs_procesar_mensajes.txt')
MAX_DELTA_SEGUNDOS_MSJ = 360

class ProcesamientoStrategy(ABC): # Hereda de ABC para ser una clase abstracta (que en este caso simula ser una interface)
    @abstractmethod # para marcar métodos que deben ser implementados obligatoriamente por las clases hijas.
    def procesar(self, procesador, mensaje: Mensaje): # los métodos abstractos no tienen implementación (solo firma)
        pass # Esto obliga a que las clases hijas implementen este método

# esto cuando llega mensaje de un docente
class ProcesamientoDocenteStrategy(ProcesamientoStrategy): # ProcesamientoDocenteStrategy hereda de ProcesamientoStrategy
    def procesar(self, procesador: ProcesadorBatch, mensaje: Mensaje):
        if procesador.preguntas_abiertas: # necesito esto también en tiempor real, pero en tiempo real son las preguntas abiertas cargadas desde la base de datos, en batch es una lista en memoria por el dataframe que se esta procesando fila por fila resulatdo de cargar un json
            procesador.contador_mensaje_respuesta += 1 # no lo necesito en tiempo real
            for pregunta in procesador.preguntas_abiertas[:]: # si necesito recorrer  preguntas abiertas en tiempo real
                pregunta.agregar_respuesta(mensaje,lista_docentes) # en batch es convertir el mensaje en un objeto Respuesta, 
                # ver si es de un docente para marcarla como validada, analizar si es corta para marcarla como tal, 
                # y agregarla a la lista de respuestas de la pregunta
                # en tiempo real necesito que se convierta en un objeto respuesta, para ver ver si es de docente
                # para marcarla como validada, ver si es corta para marcarla como tal, 
                # y también se necesita que se asociie a la pregunta pero con el id de la pregunta que se obtiene de la base de datos 
                # porque esta respuesta no queda en una lista, se debe persistir como mensaje y como respuesta en la base de datos con su id pregunta 
                logger_msj.debug(f" ✅️ Se ha agregado una nueva respuesta : {mensaje.contenido}") 
                # en tiempo real se debe utilizar otro archivo logguer que permita mostrar que se agrego una nueva respuesta 
                # pero también a qué pregunta (en texto cada uno)
                if mensaje.es_cierre_docente():
                    # también en tiempo real se debe cerrar la pregunta en la base de datos
                    procesador.cerrar_pregunta(pregunta, mensaje, motivo='docente')
                    # en el procesamiento batch cerrar_pregunta es marcar el objeto Pregunta como cerrrada, 
                    # quitarla de la lista de preguntas abiertas
                    # agregarla a la lista de preguntas cerradas y aumentar el contador de preguntas cerradas
                    # y también hacer un log de que se cerró la pregunta
                    # en tiempo real se debe marcar la pregunta como cerrada en la base de datos
                    procesador.cant_mens_cierre_docente += 1 # no lo necesito en tiempo real
        else:
            if procesador.preguntas_cerradas: 
                # en batch se tiene en memoria la lista de preguntas cerradas 
                # con el analisis del json con una serie de mensajes que se pasaron a un dataframe
                # en tiempor real se deben traer las últimas dos preguntas cerradas de la base de datos
                procesador.asociar_respuesta_a_preguntas_cerradas(mensaje,lista_docentes)
                # existe en batch y coniste en contar el mensaje como respuesta
                # y asociar la respuesta a la última o las dos últimas preguntas cerradas
                # que estan en memoria en la lista de preguntas cerrradas
                # y también hacer un log de que se asoció la respuesta a la pregunta cerrada
                # en tiempo real se debe traer las últimas dos preguntas cerradas de la base de datos
                # y asociar la respuesta a la última o las dos últimas preguntas cerradas
                # esto implica que la respuesta se debe persistir como mensaje y como respuesta en la base de datos con su id pregunta
            else:
                procesador.registrar_mensaje_suelto(mensaje)
                # en batch se cuenta el mensaje como suelto y se hace un log de que es un mensaje suelto
                # en tiempor real no deberia haber mensaje suelto, porque ya va a haber una base de datos con oreguntas ya sea abiertas o cerradas

# esto cuando llega mensaje de un alumno
class ProcesamientoAlumnoStrategy(ProcesamientoStrategy):# ProcesamientoAlumnoStrategy hereda de ProcesamientoStrategy
    def procesar(self, procesador: ProcesadorBatch, mensaje: Mensaje):
        if procesador.preguntas_abiertas:  # necesito esto también en tiempor real, pero en tiempo real son las preguntas abiertas cargadas desde la base de datos, en batch es una lista en memoria por el dataframe que se esta procesando fila por fila resulatdo de cargar un json
            autores_abiertos = {p.autor for p in procesador.preguntas_abiertas} # esta parte también va para tiempo real
            if mensaje.autor in autores_abiertos: # esta parte también va para tiempo real
                for pregunta in procesador.preguntas_abiertas[:]: # esta parte también va para tiempo real
                    if pregunta.tiene_mismo_autor(mensaje): # esta parte también va para tiempo real
                        if pregunta.es_extensible_con(mensaje, MAX_DELTA_SEGUNDOS_MSJ): # esta parte también va para tiempo real
                            pregunta.concatenar_contenido(mensaje.contenido)
                            # para batch esta definido y concatena pregunta con mensaje : def concatenar_contenido(self, nuevo_texto): self.contenido = f"{self.contenido.rstrip()} {nuevo_texto.lstrip()}"
                            # para tiempo real a partir de la pregunta abierta que se obtuvo en la base de datos, se debe actualizar el contenido de la pregunta en la base de datos concatenando el nuevo texto del mensaje  
                            logger_msj.debug(f" 📌 Se concatenó la pregunta: \n {pregunta.contenido} \n con el mensaje: {mensaje.contenido}") # también se hace log pero en archivo diferente al del batch
                            procesador.cant_concatenaciones += 1 # no se necestia en tiempo real o en todo caso enun log aparte tener cantidad de concatenaciones, nuevas pregunta o respuestas 
                        elif mensaje.es_cierre_alumno() and pregunta.tiene_respuesta_validada(): # esto tambien se necesita en tiempo real, pero supuestamente yo solo cargue preguntas en tiempo real, necesitaria cargar preguntas y respuestas y sus autores, porque s evalida los autores si son doicnetes o no de las respuestas de una pregunta, analizar o ver si cargo solo pregunta so cargar respuestas tambien con sus autores
                            procesador.cerrar_pregunta(pregunta, mensaje, motivo='alumno') # esto tambien se necesita en tiempo real pero es distinto. en tiempo real cerrar pregunta es marcarla como cerrada en la base de datos relacional
                            procesador.cant_mens_cierre_alumnos += 1 # esto no se necesita en tiempo real o en todo caso debe ir en un log algun resumen o contador 
                        else:
                            pregunta.agregar_respuesta(mensaje,lista_docentes) # en batch es convertir el mensaje en un objeto Respuesta, 
                # ver si es de un docente para marcarla como validada, analizar si es corta para marcarla como tal, 
                # y agregarla a la lista de respuestas de la pregunta
                # en tiempo real necesito que se convierta en un objeto respuesta, para ver ver si es de docente
                # para marcarla como validada, ver si es corta para marcarla como tal, 
                # y también se necesita que se asociie a la pregunta pero con el id de la pregunta que se obtiene de la base de datos 
                # porque esta respuesta no queda en una lista, se debe persistir como mensaje y como respuesta en la base de datos con su id pregunta 
                            logger_msj.debug(f" ✅️ Se ha agregado una nueva respuesta : {mensaje.contenido}") # también se hace para tiempo real pero conviene acalrar pregunta y respuestas
                            procesador.contador_mensaje_respuesta += 1 # creo que no lo necesito en tiempo real
            else:
                if mensaje.es_pregunta(): # esto si va en tiempo real
                    nueva = Pregunta(mensaje) # esto tambien va en tiempo real
                    procesador.preguntas_abiertas.append(nueva) # en tiempo real es distinto, se debe persistir la nueva prengunta en la base de datos relacional
                    procesador.contador_preguntas_nuevas += 1 # no lo necesito en tiempo real o en todo caso debe ir en un log algun resumen o contador
                    logger_msj.debug(f"🟡 NUEVA PREGUNTA: {nueva.contenido}") # si va en tiempo real pero en un log distinto 
                else:
                    procesador.contador_mensaje_respuesta += 1 # no lo necesito en tiempo real o en todo caso debe ir en un log algun resumen o contador
                     # en batch se tiene en memoria la lista de preguntas abiertas pero en tiempo real se deben traer preguntas abiertas de la base de datos relacional
                    for preg in procesador.preguntas_abiertas[:]:
                        preg.agregar_respuesta(mensaje,lista_docentes)# en batch es convertir el mensaje en un objeto Respuesta, 
                # ver si es de un docente para marcarla como validada, analizar si es corta para marcarla como tal, 
                # y agregarla a la lista de respuestas de la pregunta
                # en tiempo real necesito que se convierta en un objeto respuesta, para ver ver si es de docente
                # para marcarla como validada, ver si es corta para marcarla como tal, 
                # y también se necesita que se asociie a la pregunta pero con el id de la pregunta que se obtiene de la base de datos 
                # porque esta respuesta no queda en una lista, se debe persistir como mensaje y como respuesta en la base de datos con su id pregunta 
                        logger_msj.debug(f" ✅️ Se ha agregado una nueva respuesta : {mensaje.contenido}") # también se hace para tiempo real pero conviene aclarar pregunta y respuestas
        else:
            if mensaje.es_pregunta(): # esto si va en tiempo real
                nueva = Pregunta(mensaje) # esto también va en tiempo real
                procesador.preguntas_abiertas.append(nueva) # en tiempo real es distinto, se debe persistir la nueva prengunta en la base de datos relacional
                procesador.contador_preguntas_nuevas += 1 # no lo necesito en tiempo real o en todo caso debe ir en un log algun resumen o contador
                logger_msj.debug(f"🟡 NUEVA PREGUNTA: {nueva.contenido}") # si va en tiempo real pero en un log distinto 
            else:
                if procesador.preguntas_cerradas:
                # en batch se tiene en memoria la lista de preguntas cerradas 
                # con el analisis del json con una serie de mensajes que se pasaron a un dataframe
                # en tiempor real se deben traer las últimas dos preguntas cerradas de la base de datos
                    procesador.asociar_respuesta_a_preguntas_cerradas(mensaje,lista_docentes)
                     # existe en batch y coniste en contar el mensaje como respuesta
                    # y asociar la respuesta a la última o las dos últimas preguntas cerradas
                    # que estan en memoria en la lista de preguntas cerrradas
                    # y también hacer un log de que se asoció la respuesta a la pregunta cerrada
                    # en tiempo real se debe traer las últimas dos preguntas cerradas de la base de datos
                    # y asociar la respuesta a la última o las dos últimas preguntas cerradas
                    # esto implica que la respuesta se debe persistir como mensaje y como respuesta en la base de datos con su id pregunta
                else:
                    procesador.registrar_mensaje_suelto(mensaje)
                     # en batch se cuenta el mensaje como suelto y se hace un log de que es un mensaje suelto
                     # # en tiempor real no deberia haber mensaje suelto, porque ya va a haber una base de datos con oreguntas ya sea abiertas o cerradas

# Strategy Pattern: para separar la lógica de procesamiento de mensajes por tipo de autor 
# Separación de responsabilidades: el Procesador delega tareas específicas, lo que facilita el mantenimiento y la extensión. 
# Reutilización de procesador.procesar_mensaje(mensaje) tanto con DataFrames como con mensajes individuales en tiempo real.

# estructura de base de datos relacional
# CREATE TABLE autores (
#     id_autor SERIAL PRIMARY KEY,
#     nombre_autor TEXT NOT NULL,
#     es_docente BOOLEAN NOT NULL
# );

# CREATE TABLE mensajes (
#     id_mensaje SERIAL PRIMARY KEY,
#     id_mensaje_discord BIGINT NOT NULL,
#     autor_id INTEGER NOT NULL REFERENCES autores(id_autor) ON DELETE CASCADE,
#     fecha_mensaje TIMESTAMP NOT NULL,
#     contenido TEXT NOT NULL,
#     es_pregunta BOOLEAN DEFAULT FALSE,
#     origen TEXT
# );

# CREATE TABLE adjuntos (
#     id_adjunto SERIAL PRIMARY KEY,
#     mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
#     url TEXT NOT NULL,
#     tipo TEXT
# );

# CREATE TABLE preguntas (
#     id_pregunta SERIAL PRIMARY KEY,
#     mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
#     texto TEXT NOT NULL,
#     esta_cerrada BOOLEAN DEFAULT FALSE,
#     sin_contexto BOOLEAN DEFAULT FALSE,
#     es_administrativa BOOLEAN DEFAULT FALSE
# );

# CREATE TABLE respuestas (
#     id_respuesta SERIAL PRIMARY KEY,
#     mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
#     pregunta_id INTEGER NOT NULL REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
#     texto TEXT NOT NULL,
#     orden INTEGER,
#     es_validada BOOLEAN DEFAULT FALSE,
#     es_corta BOOLEAN DEFAULT FALSE
# );

# CREATE TABLE fragmentos_preguntas (
#     id_fragmento SERIAL PRIMARY KEY,
#     pregunta_id INTEGER NOT NULL REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
#     texto_fragmento TEXT NOT NULL,
#     orden INTEGER NOT NULL
# );

# CREATE TABLE embeddings (
#     id_embedding SERIAL PRIMARY KEY,
#     fragmento_id INTEGER NOT NULL REFERENCES fragmentos_preguntas(id_fragmento) ON DELETE CASCADE,
#     id_chroma_db TEXT NOT NULL
# );



# # persistencia de datos en la base de datos relacional desde python
# import os
# from langchain_chroma import Chroma
# from embeddings.extraer_preguntas import obtener_preguntas_y_metadatos
# from utils_for_all.utilidades_logs import setup_logger

# class GestorBaseVectorial:
#     def __init__(self, modelo, persist_directory="./chroma"):
#         self.persist_directory = persist_directory
#         self.modelo = modelo
#         self.logger_embeddings = setup_logger("logger_embeddings", "logs_generacion_embeddings.txt")
#         self.vectordb = None

#     def existe_base(self):
#         return os.path.exists(self.persist_directory) and os.listdir(self.persist_directory)
    
#     def crear_si_no_existe(self, forzar_actualizacion=False):
#         if self.existe_base() and not forzar_actualizacion:
#             self.logger_embeddings.info("✅ Usando base vectorial existente")
#             self.vectordb = Chroma(persist_directory=self.persist_directory, 
#                                 embedding_function=self.modelo)
#             return self.vectordb
        
#         # Verificar si hay datos nuevos
#         nuevas_preguntas, nuevos_metadatos = obtener_preguntas_y_metadatos()
#         if not nuevas_preguntas:
#             self.logger_embeddings.error("❌ No hay datos para crear la base vectorial")
#             return None

#         # Eliminar base existente si se fuerza actualización
#         if forzar_actualizacion and self.existe_base():
#             self.eliminar_base()

#         self.vectordb = Chroma.from_texts(
#             texts=nuevas_preguntas,
#             embedding=self.modelo,
#             metadatas=nuevos_metadatos,
#             persist_directory=self.persist_directory
#         )
#         self.logger_embeddings.info(f"🔄 Base vectorial {'actualizada' if forzar_actualizacion else 'creada'} con {len(nuevas_preguntas)} preguntas")
#         return self.vectordb

#     def buscar(self, pregunta, k=5):
#         if not self.vectordb:
#             self.logger_embeddings.error("❌ La base vectorial no está cargada.")
#             return None
        
#         try:
#             resultados = self.vectordb.similarity_search_with_score(query=pregunta, k=k)
#             resultados_con_similitud = [(doc, 1 - score) for doc, score in resultados]
#             resultados_filtrados = [(doc, sim) for doc, sim in resultados_con_similitud if sim > 0]
#             resultados_ordenados = sorted(resultados_filtrados, key=lambda x: x[1], reverse=True)
#             # def obtener_segundo(x):return x[1] y ordenados = sorted(lista, key=obtener_segundo)
#             # lambda reemplaza la definición con def
#             # sorted (secuencia_a_ordenar,criterio_de_orden,reverse= orden_ascendente_true_o_decendente_false)
            
#             self.logger_embeddings.debug(f"\n❓PREGUNTA NUEVA: {pregunta}")
#             for i, (doc, sim) in enumerate(resultados_ordenados):
#                 etiqueta = "🔝 MÁS PARECIDA:" if i == 0 else f"🔍 Resultado #{i + 1}:"
#                 self.logger_embeddings.debug(etiqueta)
#                 self.logger_embeddings.debug(f"Pregunta: {doc.page_content}")
#                 self.logger_embeddings.debug(f"Metadatos: {doc.metadata}")
#                 self.logger_embeddings.debug(f"Similitud: {sim:.4f}")
#                 self.logger_embeddings.debug("-" * 40)
            
#             if not resultados_ordenados:
#                 self.logger_embeddings.error(f"❌ No hay resultados de preguntas parecidas a la pregunta: \n  ❓'{pregunta}' ❓")
#                 return None
        
#         except Exception as e:
#             self.logger_embeddings.error(f"❌ Error en la búsqueda: {str(e)}")
#             return None
        
#     def eliminar_base(self):
#         import shutil
#         if os.path.exists(self.persist_directory):
#             shutil.rmtree(self.persist_directory)
#             self.logger_embeddings.debug("🗑️ Base vectorial eliminada.")
#         else:
#             self.logger_embeddings.debug("⚠️ No existe la base vectorial a eliminar.")
    
#     def verificar_consistencia(self):
#         """Compara conteo de preguntas en BDD vs VectorDB"""
#         preguntas_bdd, _ = obtener_preguntas_y_metadatos()
#         if not self.vectordb:
#             self.logger_embeddings.warning("⚠️ No se puede verificar consistencia: VectorDB no cargada")
#             return False
#         conteo_vectordb = self.vectordb._collection.count()
#         dif = abs(len(preguntas_bdd) - conteo_vectordb)
        
#         if dif > 0:
#             self.logger_embeddings.warning(
#                 f"🔍 Inconsistencia detectada: BDD={len(preguntas_bdd)} vs VectorDB={conteo_vectordb}"
#             )
#             return False
#         return True