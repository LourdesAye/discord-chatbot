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
        self.respuestas_sueltas = []
        self.preguntas_cerradas = []
        self.mensajes_sueltos = []

    def procesar_dataframe(self, df):
        print("🔵 Iniciando procesamiento del DataFrame...")
        for _, row in df.iterrows():
            mensaje = Mensaje.from_dataframe_row(row)
            self.procesar_mensaje(mensaje)
        print(f"✅ Procesamiento finalizado. {len(self.preguntas_abiertas)} preguntas abiertas, {len(self.preguntas_cerradas)} preguntas cerradas.")
        print(f"\n✅ Se cerraron {self.contador_preguntas} preguntas en total.\n")
        guardar_respuestas_sin_pregunta(self.respuestas_sueltas)

    def procesar_mensaje(self, mensaje: Mensaje):
        cerrar_preguntas_vencidas(self,mensaje)
        if mensaje.es_autor_docente():
            self._procesar_respuesta_docente(mensaje)
        else:
            self._procesar_mensaje_alumno(mensaje)

    def _procesar_respuesta_docente(self, mensaje: Mensaje):
        if self.preguntas_abiertas: # si hay elementos en la lista 
            for pregunta in self.preguntas_abiertas: # por cada pregunta
                if not pregunta.esta_cerrada(): # si no esta cerrada deberia sacarse
                    pregunta.agregar_respuesta(mensaje) # agrega respuesta a cada pregunta abierta
                    if mensaje.es_cierre_docente(): # si es de cierre el mensaje
                        pregunta.cerrar() # se cierra mensaje
                        self.contador_preguntas += 1  # Subo el contador
                        self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
                        self.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas
                        print(f" 🟤  Hubo un mensaje de cierre: {mensaje.contenido.lower().strip()} de docente {mensaje.autor.lower().strip()}")
                        print(" 🟢 pasó a cerrarse la pregunta por respuesta de cierre de un docente")
                        guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas)
        else:
            self.respuestas_sueltas.append(mensaje)
            print(f"🔶 Repuesta sin pregunta (no es pregunta ni respuesta): {mensaje.contenido}")

    def _procesar_mensaje_alumno(self, mensaje: Mensaje):
        # ver si hay preguntas abiertas
        # si no hay preguntas abiertas analizar si es pregunta
        # si es pregunta se guarda como pregunta en preguntas_abiertas, caso contrario se guarda en mensajes_sueltos
        # si hay preguntas abiertas
          # ver si hay alguna que es de ese autor, si es asi se asocia respuesta a su pregunta como parte del ida y vuelta con un docente
          # si no hay pregunta de él, ver si puede ser pregunta nueva de él y si no tiene aspecto de pregunta es respuesta a todas la pendiente

        if self.preguntas_abiertas: # si hay elementos en la lista 
            autores_preguntas = {pregunta.autor for pregunta in self.preguntas_abiertas} # obtengo los auores de las preguntas abiertas
            if mensaje.autor in autores_preguntas:
            # ver si hay alguna pregunta de este autor
                for pregunta in self.preguntas_abiertas: # por cada pregunta
                    if pregunta.tiene_mismo_autor(mensaje): # si el autor coincide 
                        if mensaje.es_cierre_alumno(): # si es de cierre el mensaje
                            print(f" ⚪ Hubo un mensaje de cierre : {mensaje.contenido.lower().strip()} del alumno: {mensaje.autor.lower().strip()}")
                            pregunta.cerrar() # se cierra mensaje
                            self.contador_preguntas += 1  # Subo el contador
                            self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
                            self.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas
                            print("🟢 pasó a cerrarse la pregunta por respuesta de cierre de un alumno")
                            guardar_pregunta_y_respuestas_en_log(pregunta,self.contador_preguntas)
                        else:
                            pregunta.agregar_respuesta(mensaje) # agrega como respuesta a las preguntas abiertas de ese autor
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

# Función para evaluar las preguntas abiertas
def cerrar_preguntas_vencidas(procesador: Procesador, mensaje:Mensaje):
    for pregunta in procesador.preguntas_abiertas:
        pregunta_timestamp = convertir_a_datetime(pregunta.timestamp)  # Timestamp de la pregunta original
        diferencia = tiempo_transcurrido(pregunta_timestamp, convertir_a_datetime(mensaje.timestamp))
        # Si la diferencia de tiempo supera las 36 horas, se cierra la pregunta
        if diferencia > timedelta(hours=8):
            pregunta.cerrar() # se cierra mensaje
            procesador.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
            procesador.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas 
            print("  ### pasó a cerrarse la pregunta por paso de 36 horas de pendeinte en lista de preguntas abiertas  ###")
            procesador.contador_preguntas += 1
            guardar_pregunta_y_respuestas_en_log(pregunta,procesador.contador_preguntas)