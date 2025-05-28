from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta
from datetime import timedelta
from datetime import datetime
from dateutil.parser import isoparse
from src.utils_for_all.utilidades_logs import setup_logger,guardar_pregunta_y_respuestas_en_log,guardar_respuestas_sin_pregunta
from database.knowledge_base.utils.utilidades_conversiones import convertir_a_datetime,tiempo_transcurrido
from database.knowledge_base.llm_analysis.clasificador_ia import clasificar_mensaje_y_actualizar

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
        #self.cant_consultas_llama=0

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
            self._procesar_respuesta_docente(mensaje) # _nombre_funcion: guión bajo al comienzo: la función o variable es interna y no debería ser usada fuera del módulo o clase.
        else:
            self._procesar_mensaje_alumno(mensaje)
    
    def _cerrar_pregunta_por_docente(self, pregunta: Pregunta, mensaje: Mensaje):
        self.cant_mens_cierre += 1
        pregunta.cerrar()
        self.mover_a_cerradas(pregunta)
        logger_msj.debug(f" 🟢 CIERRE DE PREGUNTA por mensaje de cierre : '{mensaje.contenido}'. DOCENTE: {mensaje.autor}")
        guardar_pregunta_y_respuestas_en_log(pregunta, self.contador_preguntas, self.nombre_log)

    def _agregar_respuesta_docente_a_preguntas_abiertas(self, mensaje: Mensaje):
        for pregunta in self.preguntas_abiertas[:]:
            pregunta.agregar_respuesta(mensaje)
            if mensaje.es_cierre_docente():
                self._cerrar_pregunta_por_docente(pregunta, mensaje)

    def _registrar_mensaje_suelto_docente(self, mensaje: Mensaje):
        self.mensajes_sueltos.append(mensaje)
        logger_msj.debug(f" 🔴 MENSAJE SIN PREGUNTAS ABIERTAS O CERRADAS : '{mensaje.contenido}'. DOCENTE:  '{mensaje.autor}' ")

    def _asociar_respuesta_a_ultimas_preguntas_cerradas(self, mensaje: Mensaje):
        ultimas_dos = self.preguntas_cerradas[-2:]
        for pregunta in ultimas_dos:
            pregunta.agregar_respuesta(mensaje)
            logger_msj.debug(f" 🔶 RESPUESTA QUE LLEGA SIN PREGUNTAS ABIERTAS: '{mensaje.contenido}'")
            logger_msj.debug(f" 🔶 SE ASOCIA A LA PREGUNTA CERRADA: '{pregunta.contenido}'")
    
    def _manejar_respuesta_docente_sin_pregunta_abierta(self, mensaje: Mensaje):
        if len(self.preguntas_cerradas) >= 2:
            self._asociar_respuesta_a_ultimas_preguntas_cerradas(mensaje)
        else:
            self._registrar_mensaje_suelto_docente(mensaje)

    def _procesar_respuesta_docente(self, mensaje: Mensaje):
        if self.preguntas_abiertas:
            self._agregar_respuesta_docente_a_preguntas_abiertas(mensaje)
        else:
            self._manejar_respuesta_docente_sin_pregunta_abierta(mensaje)

    def manejar_mensaje_sin_preguntas_previas_del_mismo_autor(self, mensaje):
        if mensaje.es_pregunta():
            nueva_pregunta = Pregunta(mensaje)
            self.preguntas_abiertas.append(nueva_pregunta)
            logger_msj.debug(f"🟡 NUEVA PREGUNTA ABIERTA: {nueva_pregunta.contenido}")
        else:
            for pregunta in self.preguntas_abiertas[:]:
                pregunta.agregar_respuesta(mensaje)
    
    def concatenar_pregunta_con_mensaje(self, pregunta, mensaje):
        pregunta_inicial = pregunta.contenido
        pregunta.concatenar_contenido(mensaje.contenido)
        logger_msj.debug( f" 🔵 LA PREGUNTA : '{pregunta_inicial}' Y EL MENSAJE: '{mensaje.contenido}' SE CONCATENARON: '{pregunta.contenido}' ")
    
    def aplicar_cierre(self,pregunta,mensaje):
        self.cant_mens_cierre += 1
        pregunta.cerrar()
        self.mover_a_cerradas(pregunta)
        logger_msj.debug(f" 🟢 CIERRE DE PREGUNTA por respuesta de cierre : {mensaje.contenido} del alumno : {mensaje.autor} ")
        guardar_pregunta_y_respuestas_en_log(pregunta, self.contador_preguntas, self.nombre_log)

    def procesar_cierre(self,pregunta,mensaje):
        if pregunta.tiene_respuesta_validada():
            self.aplicar_cierre(pregunta,mensaje)
        else:
            pregunta.agregar_respuesta(mensaje)

    def procesar_respuesta_o_cierre(self, pregunta, mensaje):
        if mensaje.es_cierre_alumno():
            self.procesar_cierre(pregunta,mensaje)
        else:
            pregunta.agregar_respuesta(mensaje)

    def manejar_mensaje_de_autor_existente(self, pregunta, mensaje):
        if  pregunta.es_extensible_con(mensaje, MAX_DELTA_SEGUNDOS_MSJ):
            self.concatenar_pregunta_con_mensaje(pregunta, mensaje)
        else:
            self.procesar_respuesta_o_cierre(pregunta, mensaje)

    def manejar_mensaje_con_preguntas_previas_del_mismo_autor(self, mensaje):
        logger_msj.debug(f"El autor '{mensaje.autor}' posee preguntas pendientes")
        # por cada pregunta en la lista de preguntas_abiertas
        for pregunta in self.preguntas_abiertas[:]:
            # si el autor del mensaje coincide con el de la pregunta
            if pregunta.tiene_mismo_autor(mensaje): 
                 self.manejar_mensaje_de_autor_existente(pregunta, mensaje)

    def procesar_mensaje_para_preguntas_abiertas(self, mensaje):
            logger_msj.debug(f" 🔢 Cantidad de Preguntas abiertas: {len(self.preguntas_abiertas)}")
            autores_preguntas_abiertas = {pregunta.autor for pregunta in self.preguntas_abiertas} # obtengo los autores de las preguntas abiertas
            # si el autor del mensaje está entre los autores de preguntas_abiertas
            if mensaje.autor in autores_preguntas_abiertas: 
                self.manejar_mensaje_con_preguntas_previas_del_mismo_autor(mensaje)
            else: # no hay preguntas pendientes de ese autor 
                self.manejar_mensaje_sin_preguntas_previas_del_mismo_autor(mensaje)
    
    def _registrar_mensaje_suelto_alumno(self, mensaje: Mensaje):
        logger_msj.debug(f"🔴 MENSAJE DE UN ALUMNO SIN PREGUNTAS ABIERTAS O CERRADAS  : '{mensaje.contenido}' ")
        self.mensajes_sueltos.append(mensaje)

    def _asociar_a_ultimas_preguntas_cerradas(self, mensaje: Mensaje):
        ultimas = self.preguntas_cerradas[-2:]
        for pregunta in ultimas:
            pregunta.agregar_respuesta(mensaje)
            logger_msj.debug(f" 🔶 RESPUESTA QUE LLEGA SIN PREGUNTAS ABIERTAS: '{mensaje.contenido}'")
            logger_msj.debug(f" 🔶 SE ASOCIA A LA PREGUNTA CERRADA: '{pregunta.contenido}'")

    def _hay_suficientes_preguntas_cerradas(self) -> bool:
        return len(self.preguntas_cerradas) >= 2

    def _manejar_mensaje_suelto_o_respuesta(self, mensaje: Mensaje):
        if self._hay_suficientes_preguntas_cerradas():
            self._asociar_a_ultimas_preguntas_cerradas(mensaje)
        else:
            self._registrar_mensaje_suelto_alumno(mensaje)


    def procesar_mensaje_pregunta(self,mensaje):
        nueva_pregunta = Pregunta(mensaje) # se crea pregunta 
        self.preguntas_abiertas.append(nueva_pregunta) # se agrega a lista de preguntas_abiertas
        logger_msj.debug(f" 🟡 Nueva Pregunta Abierta: {nueva_pregunta.contenido}")

    
    def _procesar_mensajes_sin_preguntas_abiertas(self,mensaje):
        if mensaje.es_pregunta(): # analizar si el mensaje es pregunta
            self.procesar_mensaje_pregunta(mensaje)
        else: # el mensaje no resulta ser pregunta
            self._manejar_mensaje_suelto_o_respuesta(mensaje)

            
    def _procesar_mensaje_alumno(self, mensaje: Mensaje):
        # si hay al menos 1 pregunta abierta
        if self.preguntas_abiertas: 
            self.procesar_mensaje_para_preguntas_abiertas(mensaje)
        else: # no hay preguntas abiertas
            self._procesar_mensajes_sin_preguntas_abiertas(mensaje)
    
    def mover_a_cerradas(self, pregunta):
        self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
        self.preguntas_cerradas.append(pregunta) # se agrega pregunta a lista preguntas_cerradas 
        self.contador_preguntas += 1

    def _cerrar_pregunta_por_tiempo(self, pregunta: Pregunta, mensaje: Mensaje):
        pregunta.cerrar()
        self.mover_a_cerradas(pregunta)
        logger_msj.debug(" 🟢 CIERRE DE PREGUNTA: más de 8 HORAS hay de diferencia con el mensaje actual y posee al menos una pregunta validada ###")
        logger_msj.debug(f"### NUEVO MENSAJE PARA ANALIZAR: el mensaje actual es: {mensaje.contenido} y su autor es {mensaje.autor}")
        guardar_pregunta_y_respuestas_en_log(pregunta, self.contador_preguntas, self.nombre_log)

    
    def _debe_cerrarse_por_tiempo(self, pregunta: Pregunta, mensaje_timestamp: datetime) -> bool:
        pregunta_timestamp = convertir_a_datetime(pregunta.timestamp)
        diferencia = tiempo_transcurrido(pregunta_timestamp, mensaje_timestamp)
        return diferencia > timedelta(hours=8) and pregunta.tiene_respuesta_validada()
    
    def cerrar_preguntas_por_tiempo(self, mensaje: Mensaje):
        if not self.preguntas_abiertas:
            logger_msj.debug("No hay preguntas abiertas al momento del análisis de cierre por tiempo.")
            return

        mensaje_timestamp = convertir_a_datetime(mensaje.timestamp)
        
        for pregunta in self.preguntas_abiertas[:]:
            if self._debe_cerrarse_por_tiempo(pregunta, mensaje_timestamp):
                self._cerrar_pregunta_por_tiempo(pregunta, mensaje)
    
    
    def _cerrar_pregunta_por_cantidad(self, pregunta: Pregunta, mensaje: Mensaje):
        pregunta.cerrar()
        self.mover_a_cerradas(pregunta)
        logger_msj.debug(" 🟢 CIERRE DE PREGUNTA: más de 7 respuestas y posee al menos una pregunta validada ")
        logger_msj.debug(f"### NUEVO MENSAJE PARA ANALIZAR: el mensaje actual es: {mensaje.contenido} y su autor es {mensaje.autor}")
        guardar_pregunta_y_respuestas_en_log(pregunta, self.contador_preguntas, self.nombre_log)

    def _debe_cerrarse_por_cantidad(self, pregunta: Pregunta, max_respuestas: int) -> bool:
        return len(pregunta.respuestas) >= max_respuestas and pregunta.tiene_respuesta_validada()
    
    def cerrar_preguntas_por_cantidad_mensajes(self, mensaje: Mensaje, max_mensajes_sin_respuesta: int):
        if not self.preguntas_abiertas:
            logger_msj.debug("No hay preguntas abiertas al momento del análisis por cantidad máxima superada.")
            return

        for pregunta in self.preguntas_abiertas[:]:
            if self._debe_cerrarse_por_cantidad(pregunta, max_mensajes_sin_respuesta):
                self._cerrar_pregunta_por_cantidad(pregunta, mensaje)

