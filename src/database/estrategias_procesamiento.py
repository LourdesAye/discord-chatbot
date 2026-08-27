from abc import ABC, abstractmethod # para crear clase abstracta y obligar a definir métodos a las clases hijas
from database.models.clase_mensajes import Mensaje
from database.models.clase_preguntas import Pregunta
from utils.utilidades_logs import setup_logger
from database.models.clase_autores import lista_docentes

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
    def procesar(self, procesador , mensaje: Mensaje):
        if procesador.preguntas_abiertas: # necesito esto también en tiempor real, pero en tiempo real son las preguntas abiertas cargadas desde la base de datos, en batch es una lista en memoria por el dataframe que se esta procesando fila por fila resulatdo de cargar un json
            procesador.contador_mensaje_respuesta += 1 # no lo necesito en tiempo real
            for pregunta in list(procesador.preguntas_abiertas): # si necesito recorrer  preguntas abiertas en tiempo real
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
    def procesar(self, procesador, mensaje: Mensaje):
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