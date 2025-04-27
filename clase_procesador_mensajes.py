from clase_mensajes import Mensaje
from clase_preguntas import Pregunta
from clase_respuestas import Respuesta

class Procesador:
    def __init__(self):
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

    def procesar_mensaje(self, mensaje: Mensaje):
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
                        self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
                        self.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas
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
                            pregunta.cerrar() # se cierra mensaje
                            self.preguntas_abiertas.remove(pregunta) # se quita pregunta de lista de preguntas_abiertas
                            self.preguntas_cerradas.append(pregunta)# se agrega pregunta a lista preguntas cerradas
                        else:
                            pregunta.agregar_respuesta(mensaje) # agrega como respuesta a las preguntas abiertas de ese autor
            else: # no hay preguntas pendientes de ese autor 
                for pregunta in self.preguntas_abiertas: # por cada pregunta abierta que no es del autor del mensaje
                    pregunta.agregar_respuesta(mensaje) # agrega como respuesta a las preguntas abiertas
        else: # no hay preguntas pendientes 
            if mensaje.es_pregunta():
                nueva_pregunta = Pregunta(mensaje)
                self.preguntas_abiertas.append(nueva_pregunta)
            else:
                self.mensajes_sueltos.append(mensaje)