from clase_mensajes import Mensaje
from clase_preguntas import Pregunta
from clase_respuestas import Respuesta
from datetime import datetime, timedelta
import sys

#Redirigir prints a un archivo
sys.stdout = open('log_procesamiento.txt', 'w', encoding='utf-8')

class Procesador:
    def __init__(self):
        self.contador_preguntas = 0
        self.preguntas_abiertas = []
        self.mensajes_sueltos = []
        self.preguntas_cerradas = []
        self.preguntas_a_cerrar = []
        self.contador_mensajes = 0

    def procesar_dataframe(self, df):
        print("🔵 Iniciando procesamiento del DataFrame...")
        for _, row in df.iterrows():
            self.contador_mensajes=self.contador_mensajes+1
            print()
            print(f"procesando mensaje número{self.contador_mensajes}")
            mensaje = Mensaje.from_dataframe_row(row)
            print(f"     ...   cuyo contenido es {mensaje.contenido}")
            self.procesar_mensaje(mensaje)
        print(f"✅ Procesamiento finalizado. {len(self.preguntas_abiertas)} preguntas abiertas, {len(self.preguntas_cerradas)} preguntas cerradas.")
        print(f"\n✅ Se cerraron {self.contador_preguntas} preguntas en total.\n")
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
                if mensaje.es_cierre_docente(): # si es de cierre el mensaje
                    pregunta.cerrar() # se cierra mensaje
                    self.contador_preguntas += 1  # Subo el contador
                    #puede traer conflictos lo comento y aplico la otra forma
                    #self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
                    #self.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas
                    self.preguntas_a_cerrar.append(pregunta)
                    print(f" 🟤  Hubo un mensaje de cierre: {mensaje.contenido.lower().strip()} de docente {mensaje.autor.lower().strip()}")
                    print(" 🟢 pasó a cerrarse la pregunta por respuesta de cierre de un docente")
                    guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas)
            
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
                    print(f"🔶 Mensaje dudoso asignado a la pregunta cerrada: {pregunta.contenido}")
                mensaje.es_dudoso = True  # Marcar el mensaje como dudoso
            else: 
                self.mensajes_sueltos.append(mensaje)
                print(f"🔶 Mensaje  que no posee pregunta : '{mensaje.contenido}' del docente '{mensaje.autor.lower().strip()}' ")

    def _procesar_mensaje_alumno(self, mensaje: Mensaje):
        # ver si hay preguntas abiertas
        # si no hay preguntas abiertas analizar si es pregunta
        # si es pregunta se guarda como pregunta en preguntas_abiertas, caso contrario se guarda en mensajes_sueltos
        # si hay preguntas abiertas
          # ver si hay alguna que es de ese autor, si es asi se asocia respuesta a su pregunta como parte del ida y vuelta con un docente
          # si no hay pregunta de él, ver si puede ser pregunta nueva de él y si no tiene aspecto de pregunta es respuesta a todas la pendiente
        print(f"cantidad de preguntas abiertas: {len(self.preguntas_abiertas)}")
        if self.preguntas_abiertas: # si hay elementos en la lista 
            print(f"Hay preguntas abiertas: {len(self.preguntas_abiertas)}")
            autores_preguntas = {pregunta.autor for pregunta in self.preguntas_abiertas} # obtengo los auores de las preguntas abiertas
            if mensaje.autor in autores_preguntas:
                print(f"El autor posee preguntas pendientes")
            # ver si hay alguna pregunta de este autor
                for pregunta in self.preguntas_abiertas: # por cada pregunta
                    if pregunta.tiene_mismo_autor(mensaje): # si el autor coincide 
                        if mensaje.es_cierre_alumno(): # si es de cierre el mensaje
                            print(f" ⚪ Hubo un mensaje de cierre : {mensaje.contenido.lower().strip()} del alumno: {mensaje.autor.lower().strip()}")
                            pregunta.cerrar() # se cierra mensaje
                            self.contador_preguntas += 1  # Subo el contador
                            #puede traer conflictos lo comento y aplico la otra forma
                            #self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
                            #self.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas
                            self.preguntas_a_cerrar.append(pregunta)
                            print("🟢 pasó a cerrarse la pregunta por respuesta de cierre de un alumno")
                            guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas)
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
                    print(f"🟡 Nueva Pregunta Abierta: {nueva_pregunta.contenido.lower().strip()}")
                else: # si no es pregunta se asume como respuesta a preguntas abiertas
                    for pregunta in self.preguntas_abiertas: # por cada pregunta abierta que no es del autor del mensaje
                        pregunta.agregar_respuesta(mensaje) # agrega como respuesta a las preguntas abiertas
        else: # no hay preguntas pendientes 
            if mensaje.es_pregunta():
                nueva_pregunta = Pregunta(mensaje)
                self.preguntas_abiertas.append(nueva_pregunta)
                print(f"🟡 Nueva Pregunta Abierta: {nueva_pregunta.contenido.lower().strip()}")
            else:
                if len(self.preguntas_cerradas) >= 2:
                # Tomar las dos últimas preguntas cerradas y asignar el mensaje como respuesta
                    ultimas_dos_preguntas = self.preguntas_cerradas[-2:]
                    for pregunta in ultimas_dos_preguntas:
                        pregunta.agregar_respuesta(mensaje)
                        print(f"🔶 Mensaje dudoso asignado a la pregunta cerrada: {pregunta.contenido}")
                    mensaje.es_dudoso = True  # Marcar el mensaje como dudoso
                else:
                    print(f"🔶 Mensaje de alumno que no es pregunta y no es respuesta : '{mensaje.contenido}' del docente '{mensaje.autor.lower().strip()}' ")
                    self.mensajes_sueltos.append(mensaje)

def guardar_pregunta_y_respuestas_en_log(pregunta, numero_pregunta, ruta_archivo="log_preguntas_respuestas.txt"):
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

# convertir texto a datetime
def convertir_a_datetime(cadena_fecha):
    return datetime.strptime(cadena_fecha, "%Y-%m-%dT%H:%M:%S.%fZ")

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
            print("  ### pasó a cerrarse la pregunta, más de 8 horas hay de diferencia con el mensaje actual  ###")
            print(f"         ## el mensaje actual es: {mensaje.contenido.lower().strip()} y su autor es {mensaje.autor.lower().strip()}")
            procesador.contador_preguntas += 1
            guardar_pregunta_y_respuestas_en_log(pregunta,procesador.contador_preguntas)

# Función para cerrar preguntas por tiempo o cantidad de mensajes sin respuesta
def cerrar_preguntas_por_cantidad_mensajes(procedasor: Procesador, max_mensajes_sin_respuesta):
    for pregunta in procedasor.preguntas_abiertas:
        # Verificar si la pregunta tiene más de X mensajes sin respuesta
        if len(pregunta.respuestas) >= max_mensajes_sin_respuesta:
            procedasor.preguntas_abiertas.remove(pregunta)
            procedasor.preguntas_cerradas.append(pregunta)
            print(f"Pregunta cerrada por límite de mensajes: {pregunta.contenido}")