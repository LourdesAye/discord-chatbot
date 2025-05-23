from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta
from datetime import timedelta
from dateutil.parser import isoparse
from database.knowledge_base.utils.utilidades_logs import setup_logger,guardar_pregunta_y_respuestas_en_log,guardar_respuestas_sin_pregunta
from database.knowledge_base.utils.utilidades_conversiones import convertir_a_datetime,tiempo_transcurrido

# variable para poder registrar mensajes del funcionamientos en un archivos log
logger_msj = setup_logger('procesamiento_de_mensajes','logs_procesar_mensajes.txt')

# Agregando restricciones de tiempo entre mensajes consecutivos de un mismo autor 
MAX_DELTA_SEGUNDOS_MSJ = 360

class Procesador:
    def __init__(self,nombre_log):
        self.contador_preguntas = 0
        self.preguntas_abiertas = []
        self.mensajes_sueltos = []
        self.preguntas_cerradas = []
        self.contador_mensajes = 0
        self.nombre_log= nombre_log
        self.cant_mens_cierre = 0

    def procesar_dataframe(self, df, ruta_json):
        logger_msj.debug(" 🔵 Iniciando procesamiento del DataFrame...")
        # obtener cada fila del dataframe
        for _, row in df.iterrows(): # iterrows() devuelve tupla (indice, serie). serie es un objeto que se accede como un diccionario, pero no es un diccionario
            self.contador_mensajes=self.contador_mensajes+1
            #convierte una fila (objeto serie) del dataframe en una instancia de la clase Mensaje
            mensaje = Mensaje.from_dataframe_row(row, ruta_json)
            logger_msj.debug(f" ... PROCESANDO MENSAJE {self.contador_mensajes} : '{mensaje.contenido}' ")
            self.procesar_mensaje(mensaje)
        logger_msj.debug("✅ PROCESAMIENTO FINALIZADO.")
        logger_msj.debug(f"✅ Se procesaron {self.contador_mensajes} filas" )
        logger_msj.debug(f"\n✅ Se registraron {self.contador_preguntas} preguntas en total.\n")
        logger_msj.debug(f"✅ RESULTADOS DE LISTAS: \n {len(self.preguntas_abiertas)} PREGUNTAS ABIERTAS. \n {len(self.preguntas_cerradas)} PREGUNTAS CERRADAS.")
        guardar_respuestas_sin_pregunta(self.mensajes_sueltos)
        

    def procesar_mensaje(self, mensaje: Mensaje):
        self.cerrar_preguntas_por_tiempo(mensaje)
        self.cerrar_preguntas_por_cantidad_mensajes(mensaje,7)
        if mensaje.es_autor_docente():
            logger_msj.debug("ENTRASTE ACA, IDENTIFICASTE A UN DOCENTE")
            self._procesar_respuesta_docente(mensaje) # _nombre_funcion: guión bajo al comienzo: la función o variable es interna y no debería ser usada fuera del módulo o clase.
        else:
            logger_msj.debug("ENTRASTE ACA, IDENTIFICASTE A UN ALUMNO")
            self._procesar_mensaje_alumno(mensaje)

    def _procesar_respuesta_docente(self, mensaje: Mensaje):
        if self.preguntas_abiertas: # si hay elementos en la lista preguntas_abiertas 
            logger_msj.debug("    ¡¡¡¡¡¡HAY PREGUNTAS ABIERTAS!!!!!! ")
            for pregunta in self.preguntas_abiertas[:]: # por cada pregunta en la lista
                pregunta.agregar_respuesta(mensaje) # agrega el mensaje como una respuesta y la valida si es de docente
                logger_msj.debug("    AGREGASTE RESPUESTAS A LAS PREGUNTAS ABIERTAS  ")
                if mensaje.es_cierre_docente(): # si además es de cierre el mensaje
                    ("    ENCIMA LA RESPUESTA ERA DE CIERRE  ")
                    self.cant_mens_cierre = self.cant_mens_cierre + 1
                    pregunta.cerrar() # se cierra pregunta
                    self.mover_a_cerradas(pregunta) # se quita de preguntas_abierta y se agrega a preguntas_cerradas
                    logger_msj.debug(f" 🟢 CIERRE DE PREGUNTA por mensaje de cierre : '{mensaje.contenido}'. DOCENTE: {mensaje.autor}")
                    guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas,self.nombre_log)
        else: # no hay elementos en la lista preguntas_abiertas pero llega una respuesta
            logger_msj.debug("    😵 NO,NO,NO,NO,NO,NO,NO Y NO HAY PREGUNTAS ABIERTAS 😵 PERO SI HUBO CERRADAS 😊 ")
            if len(self.preguntas_cerradas) >= 2: # se valida que la lista de preguntas_cerradas tenga al menos dos preguntas 
                ultimas_dos_preguntas = self.preguntas_cerradas[-2:] # se hace una copia de las dos últimas preguntas cerradas
                for pregunta in ultimas_dos_preguntas: # por cada una se le agrega la respuesta
                    pregunta.agregar_respuesta(mensaje)
                    logger_msj.debug(f" 🔶 RESPUESTA QUE LLEGA SIN PREGUNTAS ABIERTAS: '{mensaje.contenido}'")
                    logger_msj.debug(f" 🔶 SE ASOCIA A LA PREGUNTA CERRADA: '{pregunta.contenido}'")
            else: # si la lista de preguntas_cerradas no posee al menos dos preguntas
                logger_msj.debug("    😵 NO,NO,NO,NO,NO,NO,NO Y NO HAY PREGUNTAS ABIERTAS 😵 Y ENCIMA NO HAY PREGUNTAS CERRADAS 😭")
                self.mensajes_sueltos.append(mensaje) # se agrega mensaje a lista de mensajes_sueltos (no son pregunta ni respuesta)
                logger_msj.debug(f" 🔴 MENSAJE SIN PREGUNTAS ABIERTAS O CERRADAS : '{mensaje.contenido}'. DOCENTE:  '{mensaje.autor}' ")

    def _procesar_mensaje_alumno(self, mensaje: Mensaje):
        # si hay al menos 1 pregunta abierta
        if self.preguntas_abiertas: 
            logger_msj.debug("    ¡¡¡¡¡¡HAY PREGUNTAS ABIERTAS!!!!!! ")
            logger_msj.debug(f" 🔢 Cantidad de Preguntas abiertas: {len(self.preguntas_abiertas)}")
            autores_preguntas_abiertas = {pregunta.autor for pregunta in self.preguntas_abiertas} # obtengo los autores de las preguntas abiertas
            # si el autor del mensaje está entre los autores de preguntas_abiertas
            if mensaje.autor in autores_preguntas_abiertas: 
                logger_msj.debug(f"El autor '{mensaje.autor}' posee preguntas pendientes")
                # por cada pregunta en la lista de preguntas_abiertas
                for pregunta in self.preguntas_abiertas[:]:
                    # si el autor del mensaje coincide con el de la pregunta
                    if pregunta.tiene_mismo_autor(mensaje): 
                        # y si pregunta no tiene respuestas y el mensaje es cercano en el tiempo
                        if not pregunta.tiene_respuestas() and pregunta.es_cercana_en_tiempo(mensaje,MAX_DELTA_SEGUNDOS_MSJ):
                            pregunta_inicial = pregunta.contenido
                            pregunta.concatenar_contenido(mensaje.contenido) # se concatena pregunta con mensaje
                            logger_msj.debug(f" 🔵 LA PREGUNTA : '{pregunta_inicial}' Y EL MENSAJE: '{mensaje.contenido}' SE CONCATENARON: '{pregunta.contenido}' ")
                        else: 
                        # y si la pregunta posee al menos una respuesta y/o es lejano en el tiempo
                            # se analiza si el mensaje es de cierre 
                            if mensaje.es_cierre_alumno():
                                # y si además la pregunta tiene al menos una respuesta validada 
                                if pregunta.tiene_respuesta_validada():
                                    self.cant_mens_cierre= self.cant_mens_cierre +1 # se cuentan las frases de cierre
                                    pregunta.cerrar() # se cierra pregunta 
                                    self.mover_a_cerradas(pregunta) # pregunta se saca de lista preguntas_abiertas y se pone en lista de preguntas_cerradas
                                    logger_msj.debug(f" 🟢 CIERRE DE PREGUNTA por respuesta de cierre : {mensaje.contenido} del alumno : {mensaje.autor} ")
                                    guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas,self.nombre_log)
                                # la pregunta no tiene respuestas validadas 
                                else: 
                                    pregunta.agregar_respuesta(mensaje) # agrega como respuesta a las preguntas abiertas de ese autor
                            # el mensaje no es de cierre
                            else:
                                pregunta.agregar_respuesta(mensaje) # agrega como respuesta a las preguntas abiertas de ese autor
            else: # no hay preguntas pendientes de ese autor 
                if mensaje.es_pregunta(): # se analiza si mensaje puede ser pregunta
                    nueva_pregunta = Pregunta(mensaje) # se convierte mensaje en pregunta
                    self.preguntas_abiertas.append(nueva_pregunta) # pregunta pasa a lista de preguntas_abiertas
                    logger_msj.debug(f" 🟡 NUEVA PREGUNTA ABIERTA: {nueva_pregunta.contenido}")
                else: # si no es pregunta se asume como respuesta a preguntas abiertas
                    for pregunta in self.preguntas_abiertas[:]: # por cada pregunta abierta que no es del autor del mensaje
                        pregunta.agregar_respuesta(mensaje) # agrega como respuesta a las preguntas abiertas
        else: # no hay preguntas abiertas
            logger_msj.debug("    😵 NO,NO,NO,NO,NO,NO,NO Y NO HAY PREGUNTAS ABIERTAS 😵  ¿¿¿¿¿¿¿MENSAJE ES PREGUNTA O ES RESPUESTA????? 🤔🤔🤔 ")
            if mensaje.es_pregunta(): # analizar si el mensaje es pregunta
                logger_msj.debug("  MENSAJE ES PREGUNTA 😊 We are the champions 🏆🏆🏆🏆 ")
                nueva_pregunta = Pregunta(mensaje) # se crea pregunta 
                self.preguntas_abiertas.append(nueva_pregunta) # se agrega a lista de preguntas_abiertas
                logger_msj.debug(f" 🟡 Nueva Pregunta Abierta: {nueva_pregunta.contenido}")
            else: # el mensaje no resulta ser pregunta
                logger_msj.debug("  MENSAJE ES RESPUESTA 👀 ") 
                if len(self.preguntas_cerradas) >= 2: # evaluar si hay al menos 2 preguntas cerradas
                    logger_msj.debug("  HAY AL MENOS DOS PREGUNTAS CERRADAS ") 
                    ultimas_dos_preguntas = self.preguntas_cerradas[-2:] # se hace una copia de las dos últimas preguntas cerradas
                    for pregunta in ultimas_dos_preguntas:
                        pregunta.agregar_respuesta(mensaje) # se agrega respuesta a las últimas preguntas cerradas
                        logger_msj.debug(f" 🔶 RESPUESTA QUE LLEGA SIN PREGUNTAS ABIERTAS: '{mensaje.contenido}'")
                        logger_msj.debug(f" 🔶 SE ASOCIA A LA PREGUNTA CERRADA: '{pregunta.contenido}'")
                else: # no hay al menos dos preguntas cerradas
                    logger_msj.debug("  MENSAJE ES RESPUESTA 👀 Y NO,NO,NO,NO,NO,NO,NO HAY PREGUNTAS CERRADAS!!!!!! CUIDADO ACA!!!!!!! ") 
                    logger_msj.debug(f"🔴 MENSAJE DE UN ALUMNO SIN PREGUNTAS ABIERTAS O CERRDAS  : '{mensaje.contenido}' ")
                    self.mensajes_sueltos.append(mensaje)
    
    def mover_a_cerradas(self, pregunta):
        self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
        self.preguntas_cerradas.append(pregunta) # se agrega pregunta a lista preguntas_cerradas 
        self.contador_preguntas += 1

    #  Función para cerrar preguntas abiertas por diferencia de tiempo entre el mensaje a analizar y las preguntas pendientes de cierre 
    def cerrar_preguntas_por_tiempo(self, mensaje:Mensaje):
        if not self.preguntas_abiertas:
            logger_msj.debug("No hay preguntas abiertas al momento del análisis de cierre por tiempo.")
            return
        mensaje_timestamp =convertir_a_datetime(mensaje.timestamp)
        for pregunta in self.preguntas_abiertas[:]:  # [:]: eso es copia superficial de la original 
            pregunta_timestamp = convertir_a_datetime(pregunta.timestamp)  # timestamp de la pregunta que esta abierta en la lista
            diferencia_de_tiempo = tiempo_transcurrido(pregunta_timestamp, mensaje_timestamp)
            # Si la diferencia de tiempo supera las 8 horas y además la pregunta tiene al menos una respuesta validada
            if diferencia_de_tiempo > timedelta(hours=8) and pregunta.tiene_respuesta_validada():
                pregunta.cerrar() # se marcan como cerradas las preguntas abiertas que cumplan con el criterio 
                self.mover_a_cerradas(pregunta)
                logger_msj.debug(" 🟢 CIERRE DE PREGUNTA: más de 8 HORAS hay de diferencia con el mensaje actual y posee al menos una pregunta validada ###")
                logger_msj.debug(f"### NUEVO MENSAJE PARA ANALIZAR: el mensaje actual es: {mensaje.contenido} y su autor es {mensaje.autor}")
                guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas,self.nombre_log)

    # Función para cerrar preguntas por tiempo o cantidad de mensajes sin respuesta
    def cerrar_preguntas_por_cantidad_mensajes(self, mensaje:Mensaje, max_mensajes_sin_respuesta):
        if not self.preguntas_abiertas:
            logger_msj.debug("No hay preguntas abiertas al momento del análisis por cantidad máxima superada.")
            return
        for pregunta in self.preguntas_abiertas[:]: # [:]: eso es copia de la original para iterar sobre ella y evitar errores en tiempo de ejecución
            if len(pregunta.respuestas) >= max_mensajes_sin_respuesta and pregunta.tiene_respuesta_validada():
                pregunta.cerrar()
                self.mover_a_cerradas(pregunta)
                logger_msj.debug(f" 🟢 CIERRE DE PREGUNTA: más de 7 respuestas y posee al menos una pregunta validada ")
                logger_msj.debug(f"### NUEVO MENSAJE PARA ANALIZAR: el mensaje actual es: {mensaje.contenido} y su autor es {mensaje.autor}")
                guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas,self.nombre_log)

