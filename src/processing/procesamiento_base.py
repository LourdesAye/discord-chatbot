from database.models.clase_mensajes import Mensaje
from database.models.clase_preguntas import Pregunta
from utils.utilidades_logs import setup_logger, guardar_pregunta_y_respuestas_en_log
from database.utilidades_conversiones import convertir_a_datetime, tiempo_transcurrido
from datetime import timedelta
from database.database.services.estrategias_procesamiento import ProcesamientoAlumnoStrategy,ProcesamientoDocenteStrategy
from database.models.clase_autores import lista_docentes

logger_msj = setup_logger('procesamiento_de_mensajes', 'logs_procesar_mensajes.txt')
MAX_RESPUESTAS = 7
TIEMPO_CIERRE_HORAS = 8

class Procesador:
    def __init__(self, nombre_log, estrategias=None):
        self.nombre_log = nombre_log
        self.preguntas_abiertas = []
        self.preguntas_cerradas = []
        self.mensajes_sueltos = []
        self.contador_mensajes = 0
        self.contador_preguntas_nuevas = 0
        self.contador_preguntas_cerradas = 0
        self.cant_concatenaciones = 0
        self.contador_mensaje_respuesta = 0
        self.cant_mens_cierre_alumnos = 0
        self.cant_mens_cierre_docente = 0

        self.estrategias = estrategias or {
            'docente': ProcesamientoDocenteStrategy(),
            'alumno': ProcesamientoAlumnoStrategy()
        }

    def procesar_dataframe(self, df, ruta_json):
        logger_msj.debug(" 🔵 Iniciando procesamiento del DataFrame...")
        for _, row in df.iterrows():
            mensaje = Mensaje.from_dataframe_row(row, ruta_json)
            self.contador_mensajes += 1
            logger_msj.debug(f" ... PROCESANDO MENSAJE {self.contador_mensajes}: '{mensaje.contenido}' ")
            self.cerrar_por_reglas(mensaje)
            self.procesar_mensaje(mensaje)
        logger_msj.debug("✅ PROCESAMIENTO FINALIZADO.")
        for numero_pregunta,pregunta in enumerate(self.preguntas_cerradas,start=1):
            guardar_pregunta_y_respuestas_en_log(pregunta, numero_pregunta,self.nombre_log)
        logger_msj.debug(f"Total mensajes: {self.contador_mensajes}, Preguntas nuevas: {self.contador_preguntas_nuevas}, Cerradas: {self.contador_preguntas_cerradas}")

    def procesar_mensaje(self, mensaje: Mensaje):
        tipo = 'docente' if mensaje.es_autor_docente() else 'alumno'
        self.estrategias[tipo].procesar(self, mensaje)

    def cerrar_por_reglas(self, mensaje: Mensaje):
        ahora = convertir_a_datetime(mensaje.timestamp)
        for pregunta in self.preguntas_abiertas[:]:
            tiempo = tiempo_transcurrido(convertir_a_datetime(pregunta.timestamp), ahora)
            if pregunta.tiene_respuesta_validada():
                if tiempo > timedelta(hours=TIEMPO_CIERRE_HORAS):
                    self.cerrar_pregunta(pregunta, mensaje, motivo='tiempo')
                elif len(pregunta.respuestas) >= MAX_RESPUESTAS:
                    self.cerrar_pregunta(pregunta, mensaje, motivo='cantidad')

    def cerrar_pregunta(self, pregunta: Pregunta, mensaje: Mensaje, motivo=None):
        pregunta.cerrar()
        self.preguntas_abiertas.remove(pregunta)
        self.preguntas_cerradas.append(pregunta)
        self.contador_preguntas_cerradas += 1
        logger_msj.debug(f"🟢 PREGUNTA CERRADA por {motivo}")

    def registrar_mensaje_suelto(self, mensaje: Mensaje):
            self.mensajes_sueltos.append(mensaje)
            autor_tipo = "DOCENTE" if mensaje.es_autor_docente() else "ALUMNO"
            logger_msj.debug(f" 🔴 MENSAJE SUELTO: '{mensaje.contenido}' de {autor_tipo} : {mensaje.autor} ")

    def asociar_respuesta_a_preguntas_cerradas(self, mensaje, lista_docentes):
        self.contador_mensaje_respuesta += 1
        cantidad = len(self.preguntas_cerradas)
        preguntas_a_asociar = (
            self.preguntas_cerradas[-1:]
            if cantidad == 1
            else self.preguntas_cerradas[-2:]
        )
        for pregunta in preguntas_a_asociar:
            pregunta.agregar_respuesta(mensaje, lista_docentes)
            logger_msj.debug(f" 🔶 RESPUESTA QUE LLEGA SIN PREGUNTAS ABIERTAS: '{mensaje.contenido}'")
            logger_msj.debug(f" 🔶 SE ASOCIA A LA PREGUNTA CERRADA: '{pregunta.contenido}'")
