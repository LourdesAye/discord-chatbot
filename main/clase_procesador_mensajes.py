from main.clase_mensajes import Mensaje
from main.clase_preguntas import Pregunta
from main.clase_respuestas import Respuesta
from datetime import datetime, timedelta
import sys
from dateutil.parser import isoparse
from utilidades.utilidades_logs import setup_logger
from datetime import datetime
from dateutil.parser import parse as parse_date

# Redirigir prints a un archivo
logger_msj = setup_logger('proc_mensaj','logs_procesar_mensajes.txt')
logger_preg_unificadas = setup_logger('unif_preg','log_preguntas_unificadas.txt')

# Agregando restricciones de tiempo entre mensajes consecutivos de un mismo autor 
MAX_DELTA_SEGUNDOS_MSJ = 360

# convertir texto a datetime
def convertir_a_datetime(cadena_fecha):
      return isoparse(cadena_fecha) # convierte la cadena en un objeto datetime

class Procesador:
    def __init__(self,nombre_log):
        self.contador_preguntas = 0
        self.preguntas_abiertas = []
        self.mensajes_sueltos = []
        self.preguntas_cerradas = []
        self.preguntas_a_cerrar = []
        self.contador_mensajes = 0
        self.nombre_log= nombre_log
        self.contador_de_preguntas_ajustadas=0
        self.cant_mens_cierre = 0
        self.registros_procesados = 0
        self.mensajes_validados=0
      
    def transformar_respuesta(self,pregunta_anterior, pregunta):
        mensaje_nuevo = Mensaje(pregunta.id_pregunta,pregunta.autor,pregunta.contenido,pregunta.timestamp,pregunta.attachments,pregunta.origen)
        respuesta_nueva = Respuesta(mensaje_nuevo)
        pregunta_anterior.respuestas.append(respuesta_nueva)
        pregunta_anterior.respuestas.extend(pregunta.respuestas) # Agregar también sus respuestas (si las tenía)


    def procesar_preguntas_cortas(self, preguntas_cerradas):
        logger_msj.debug("Se van a procesar preguntas cortas de las preguntas cerradas")
        preguntas_cerradas.sort(key=lambda p: convertir_a_datetime(p.timestamp))
        logger_msj.debug("1. Se ordenaron las preguntas cerradas por fecha antigua a más actual")
        
        preguntas_filtradas = []
        transformadas = 0

        for i in range(len(preguntas_cerradas)):
            pregunta = preguntas_cerradas[i]
            palabras = pregunta.contenido.strip().split()

            if len(palabras) <= 4:
                logger_msj.debug(f"2. Se detectó pregunta corta: {pregunta.contenido}")
                encontrada_padre= False

                # Buscar hacia atrás una pregunta válida del mismo autor
                for j in range(i - 1, -1, -1):
                    posible_padre = preguntas_cerradas[j]

                    if posible_padre.autor.lower().strip() == pregunta.autor.lower().strip():
                        logger_preg_unificadas.debug("LAS PREGUNTAS CONVERTIDAS EN RESPUESTA POR FALTA DE CONTEXTO:")
                        logger_preg_unificadas.debug(f" PREGUNTA PADRE {j+1} : {posible_padre.contenido}")
                        logger_preg_unificadas.debug(f" PREGUNTA A CONVERTIR EN RESPUESTA: {i+1} : {pregunta.contenido}")
                        logger_msj.debug(f"3. Se encontró pregunta previa del mismo autor: '{posible_padre.contenido}'")
                        logger_msj.debug(f"   esa pregunta poseee {len(posible_padre.respuestas)} respuestas")
                        self.transformar_respuesta(posible_padre, pregunta)
                        logger_msj.debug(f"   Se van a sumar {len(pregunta.respuestas) + 1} respuestas")
                        logger_msj.debug(f"   Se agregó como respuesta: '{pregunta.contenido}' y otras")
                        logger_msj.debug(f"   Ahora la cantidad de respuestas: {len(posible_padre.respuestas)}")
                        transformadas += 1
                        encontrada_padre = True
                        self.contador_de_preguntas_ajustadas=self.contador_de_preguntas_ajustadas + 1
                        break  # Ya se transformó, salgo del for interno      
                
                if not encontrada_padre:
                # No se encontró pregunta anterior del mismo autor → se queda como pregunta
                    preguntas_filtradas.append(pregunta)  
            else:
            # Pregunta larga → se queda como está
                preguntas_filtradas.append(pregunta)
        
        preguntas_cerradas[:] = preguntas_filtradas
        logger_msj.debug(f"Preguntas transformadas en respuesta: {transformadas}")
        logger_msj.debug(f"Preguntas finales para procesar: {len(preguntas_cerradas)}")

    
    def procesar_dataframe(self, df, ruta_json):
        logger_msj.debug("🔵 Iniciando procesamiento del DataFrame...")
        # obtener cada fila del dataframe
        for _, row in df.iterrows(): # iterrows() devuelve tupla (indice, serie). serie es un objeto que se accede como un diccionario, pero no es un diccionario
            self.contador_mensajes=self.contador_mensajes+1
            logger_msj.debug(f"procesando mensaje número{self.contador_mensajes}")
            #convierte una fila (objeto serie) del dataframe en una instancia de la clase Mensaje
            mensaje = Mensaje.from_dataframe_row(row, ruta_json)
            logger_msj.debug(f"     ...   cuyo contenido es {mensaje.contenido}")
            self.procesar_mensaje(mensaje)
        logger_msj.debug(f"✅ Se procesaron {self.contador_mensajes} filas" )
        #self.procesar_preguntas_cortas(self.preguntas_cerradas)
        logger_msj.debug(f"\n✅ Se registraron {self.contador_preguntas} preguntas en total.\n")
        logger_msj.debug(f"✅ Procesamiento finalizado. {len(self.preguntas_abiertas)} preguntas abiertas, {len(self.preguntas_cerradas)} preguntas cerradas.")
        guardar_respuestas_sin_pregunta(self.mensajes_sueltos)
        

    def procesar_mensaje(self, mensaje: Mensaje):
        cerrar_preguntas_por_tiempo(self,mensaje)
        cerrar_preguntas_por_cantidad_mensajes(self,7)
        if mensaje.es_autor_docente():
            self._procesar_respuesta_docente(mensaje)
        else:
            self._procesar_mensaje_alumno(mensaje)

    def _procesar_respuesta_docente(self, mensaje: Mensaje):
        if self.preguntas_abiertas: # si hay elementos en la lista 
            for pregunta in self.preguntas_abiertas: # por cada pregunta
                pregunta.agregar_respuesta(mensaje) # agrega respuesta a cada pregunta abierta
                # aca deberia poner a la respuesta que es validada
                if mensaje.es_cierre_docente(): # si es de cierre el mensaje
                    # logger_resp_validadas.debug("Cierre de docente ")
                    # respuesta_a_validar = pregunta.obtener_ultima_respuesta_no_docente(mensaje)  # creás este método en la clase Pregunta
                    # if respuesta_a_validar:
                    #     self.mensajes_validados=self.mensajes_validados+1
                    #     logger_resp_validadas.debug(f"respuesta validada {self.mensajes_validados} : {respuesta_a_validar.contenido} es del alumno : {respuesta_a_validar.autor}")
                    #     respuesta_a_validar.es_validada = True
                    self.cant_mens_cierre = self.cant_mens_cierre + 1
                    pregunta.cerrar() # se cierra mensaje
                    self.contador_preguntas += 1  # Subo el contador
                    #puede traer conflictos lo comento y aplico la otra forma
                    #self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
                    #self.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas
                    self.preguntas_a_cerrar.append(pregunta)
                    logger_msj.debug(f"🟤  Hubo un mensaje de cierre: {mensaje.contenido.lower().strip()} de docente {mensaje.autor.lower().strip()}")
                    logger_msj.debug("🟢 pasó a cerrarse la pregunta por respuesta de cierre de un docente")
                    guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas,self.nombre_log)

            
            for pregunta in self.preguntas_a_cerrar:
                if pregunta in self.preguntas_abiertas:  # Verifica si existe antes de eliminar
                    self.preguntas_abiertas.remove(pregunta)
                    self.preguntas_cerradas.append(pregunta)
        else:
            # Si no hay preguntas abiertas, asignar el mensaje como "dudoso" y asignar como respuesta a las dos últimas preguntas cerradas
            if len(self.preguntas_cerradas) >= 2:
                # Tomar las dos últimas preguntas cerradas
                ultimas_dos_preguntas = self.preguntas_cerradas[-2:]
                for pregunta in ultimas_dos_preguntas:
                    pregunta.agregar_respuesta(mensaje)
                    logger_msj.debug(f"  🔶 Mensaje dudoso asignado a la pregunta cerrada: {pregunta.contenido}")
                # mensaje.es_dudoso = True  # Marcar el mensaje como dudoso
            else: 
                self.mensajes_sueltos.append(mensaje)
                logger_msj.debug(f"  🔶 Mensaje  que no posee pregunta : '{mensaje.contenido}' del docente '{mensaje.autor.lower().strip()}' ")

    def _procesar_mensaje_alumno(self, mensaje: Mensaje):
        # ver si hay preguntas abiertas
        # si no hay preguntas abiertas analizar si es pregunta
        # si es pregunta se guarda como pregunta en preguntas_abiertas, caso contrario se guarda en mensajes_sueltos
        # si hay preguntas abiertas
          # ver si hay alguna que es de ese autor, si es asi se asocia respuesta a su pregunta como parte del ida y vuelta con un docente
          # si no hay pregunta de él, ver si puede ser pregunta nueva de él y si no tiene aspecto de pregunta es respuesta a todas la pendiente
        logger_msj.debug(f"cantidad de preguntas abiertas: {len(self.preguntas_abiertas)}")
        if self.preguntas_abiertas: # si hay elementos en la lista 
            
            # detección manual de dos preguntas por revisión
            # if mensaje.es_pregunta_reconocida_manual(): # preguntas reconocidas manualmente por pruebas de muestreo
            #     preguntas_a_cerrar = list(self.preguntas_abiertas)  # se copia la lista de preguntas abiertas que se deben cerrar
            #     for pregunta in preguntas_a_cerrar: # se cierran las preguntas
            #         pregunta.cerrar()
            #         self.contador_preguntas += 1 # contando las pregunta cerradas
            #         self.preguntas_abiertas.remove(pregunta) # se eliminan de lista de preguntas abiertas
            #         self.preguntas_cerradas.append(pregunta) # se agregan a lista de preguntas cerradas
            #     nueva_pregunta = Pregunta(mensaje) # se da origen a una nueva pregunta
            #     self.preguntas_abiertas.append(nueva_pregunta) # se agrega a lista de preguntas abiertas
            #     logger_msj.debug(f"🟡 Nueva Pregunta Abierta (manual): {nueva_pregunta.contenido.lower().strip()}")  
            # else:
            
                logger_msj.debug(f"Hay preguntas abiertas: {len(self.preguntas_abiertas)}")
                autores_preguntas = {pregunta.autor for pregunta in self.preguntas_abiertas} # obtengo los autores de las preguntas abiertas
                if mensaje.autor in autores_preguntas:
                    logger_msj.debug(f"El autor posee preguntas pendientes")
                # ver si hay alguna pregunta de este autor
                    for pregunta in self.preguntas_abiertas: # por cada pregunta
                        if pregunta.tiene_mismo_autor(mensaje): # si el autor coincide 
                            # si pregunta almacenada en preguntas_abiertas tiene mismo autor que el mensaje, no tiene respuestas y es relativamente cercana
                            if not pregunta.tiene_respuestas() and (convertir_a_datetime(mensaje.timestamp) - convertir_a_datetime(pregunta.timestamp)).total_seconds() < MAX_DELTA_SEGUNDOS_MSJ:
                                # se concatena pregunta con mensaje
                                pregunta.concatenar_contenido(mensaje.contenido)
                                logger_msj.debug(f"🔵 El mensaje fue concatenado a la pregunta anterior: {pregunta.contenido}")
                            else:
                            # si la pregunta almacenada en preguntas_abiertas tiene el mismo autor que el mensaje
                            # pero el mensaje o tiene respuesta o es lejano en el tiempo: se mira si es cierre de alumno
                                if mensaje.es_cierre_alumno(): # si es de cierre el mensaje
                                    self.cant_mens_cierre= self.cant_mens_cierre +1
                                    logger_msj.debug(f"⚪ Hubo un mensaje de cierre : {mensaje.contenido.lower().strip()} del alumno: {mensaje.autor.lower().strip()}")
                                    pregunta.cerrar() # se cierra mensaje
                                    self.contador_preguntas += 1  # Subo el contador
                                    #puede traer conflictos lo comento y aplico la otra forma
                                    #self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
                                    #self.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas
                                    self.preguntas_a_cerrar.append(pregunta)
                                    logger_msj.debug("🟢 pasó a cerrarse la pregunta por respuesta de cierre de un alumno")
                                    guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas,self.nombre_log)
                                else:
                                    pregunta.agregar_respuesta(mensaje) # agrega como respuesta a las preguntas abiertas de ese autor
                    for pregunta in self.preguntas_a_cerrar:
                        if pregunta in self.preguntas_abiertas:  # Verifica si existe antes de eliminar
                            self.preguntas_abiertas.remove(pregunta)
                            self.preguntas_cerradas.append(pregunta)
                else: # no hay preguntas pendientes de ese autor 
                    if mensaje.es_pregunta(): # ese mensaje puede ser pregunta o respuesta
                        nueva_pregunta = Pregunta(mensaje)
                        self.preguntas_abiertas.append(nueva_pregunta)
                        logger_msj.debug(f"🟡 Nueva Pregunta Abierta: {nueva_pregunta.contenido.lower().strip()}")
                    else: # si no es pregunta se asume como respuesta a preguntas abiertas
                        for pregunta in self.preguntas_abiertas: # por cada pregunta abierta que no es del autor del mensaje
                            pregunta.agregar_respuesta(mensaje) # agrega como respuesta a las preguntas abiertas
        else: # no hay preguntas pendientes 
            if mensaje.es_pregunta():
                nueva_pregunta = Pregunta(mensaje)
                self.preguntas_abiertas.append(nueva_pregunta)
                logger_msj.debug(f"🟡 Nueva Pregunta Abierta: {nueva_pregunta.contenido.lower().strip()}")
            else:
                if len(self.preguntas_cerradas) >= 2:
                # Tomar las dos últimas preguntas cerradas y asignar el mensaje como respuesta
                    ultimas_dos_preguntas = self.preguntas_cerradas[-2:]
                    for pregunta in ultimas_dos_preguntas:
                        pregunta.agregar_respuesta(mensaje)
                        logger_msj.debug(f"🔶 Mensaje dudoso asignado a la pregunta cerrada: {pregunta.contenido}")
                    mensaje.es_dudoso = True  # Marcar el mensaje como dudoso
                else:
                    logger_msj.debug(f"🔶 Mensaje de alumno que no es pregunta y no es respuesta : '{mensaje.contenido}' del docente '{mensaje.autor.lower().strip()}' ")
                    self.mensajes_sueltos.append(mensaje)



def guardar_pregunta_y_respuestas_en_log(pregunta, numero_pregunta, ruta_archivo):
    with open(ruta_archivo, "a", encoding="utf-8") as f:
        f.write("═══════════════════════════════════════════════════════\n")
        f.write(f"[PREGUNTA {numero_pregunta}]\n")
        f.write(pregunta.contenido + "\n")
        f.write(pregunta.timestamp + "\n")
        f.write("\n[RESPUESTAS]\n")
        if pregunta.respuestas:
            for idx, respuesta in enumerate(pregunta.respuestas, start=1):
                f.write(f"  → Fecha de Respuesta {idx}: {respuesta.timestamp}\n")
                f.write(f"      → Autor Respuesta {idx}: {respuesta.autor}\n")
                f.write(f"          → Respuesta {idx}: {respuesta.contenido}\n")
        else:
            f.write("⚠️ No hubo respuestas para esta pregunta.\n")
        f.write("═══════════════════════════════════════════════════════\n\n")

def guardar_respuestas_sin_pregunta(respuestas_huerfanas, ruta_archivo="log_respuestas_sin_pregunta.txt"):
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write("═══════════════════════════════════════════════════════\n")
        f.write("LOG DE RESPUESTAS SIN PREGUNTA\n")
        f.write("═══════════════════════════════════════════════════════\n\n")
        
        if not respuestas_huerfanas:
            f.write("✅ No quedaron respuestas sin pregunta.\n")
        else:
            for idx, respuesta in enumerate(respuestas_huerfanas, start=1):
                f.write(f"[RESPUESTA {idx}]\n")
                f.write(f"Fecha: {respuesta.timestamp}\n")
                f.write(f"Autor: {respuesta.autor}\n")
                f.write(f"Contenido: {respuesta.contenido}\n")
                f.write("-------------------------------------------------------\n\n")



# Función para calcular la diferencia de tiempo
def tiempo_transcurrido(pregunta_timestamp, mensaje_timestamp):
    return mensaje_timestamp - pregunta_timestamp

#  Función para cerrar preguntas por tiempo 
def cerrar_preguntas_por_tiempo(procesador: Procesador, mensaje:Mensaje):
    for pregunta in procesador.preguntas_abiertas:
        pregunta_timestamp = convertir_a_datetime(pregunta.timestamp)  # Timestamp de la pregunta original
        diferencia = tiempo_transcurrido(pregunta_timestamp, convertir_a_datetime(mensaje.timestamp))
        # Si la diferencia de tiempo supera las 36 horas, se cierra la pregunta
        if diferencia > timedelta(hours=8) and len(pregunta.respuestas) > 0:
            pregunta.cerrar() # se cierra mensaje
            procesador.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
            procesador.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas 
            logger_msj.debug("  ### pasó a cerrarse la pregunta, más de 8 horas hay de diferencia con el mensaje actual  ###")
            logger_msj.debug(f"         ## el mensaje actual es: {mensaje.contenido.lower().strip()} y su autor es {mensaje.autor.lower().strip()}")
            procesador.contador_preguntas += 1
            guardar_pregunta_y_respuestas_en_log(pregunta,procesador.contador_preguntas,procesador.nombre_log)

# Función para cerrar preguntas por tiempo o cantidad de mensajes sin respuesta
def cerrar_preguntas_por_cantidad_mensajes(procesador: Procesador, max_mensajes_sin_respuesta):
    for pregunta in procesador.preguntas_abiertas:
        # Verificar si la pregunta tiene más de X mensajes sin respuesta
        if len(pregunta.respuestas) >= max_mensajes_sin_respuesta:
            pregunta.cerrar()
            procesador.contador_preguntas=procesador.contador_preguntas + 1
            procesador.preguntas_abiertas.remove(pregunta)
            procesador.preguntas_cerradas.append(pregunta)
            logger_msj.debug(f"Pregunta cerrada por límite de mensajes: {pregunta.contenido}")
            guardar_pregunta_y_respuestas_en_log(pregunta,procesador.contador_preguntas,procesador.nombre_log)

