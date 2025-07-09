from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta
from utils_for_all.utilidades_logs import setup_logger, guardar_pregunta_y_respuestas_en_log, guardar_respuestas_sin_pregunta
from database.knowledge_base.utils.utilidades_conversiones import convertir_a_datetime, tiempo_transcurrido
from datetime import timedelta
from database.knowledge_base.services.estrategias_procesamiento import ProcesamientoAlumnoStrategy,ProcesamientoDocenteStrategy
from database.knowledge_base.models.clase_autores import lista_docentes

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
        logger_msj.debug(f"Total mensajes: {self.contador_mensajes}, Preguntas nuevas: {self.contador_preguntas_nuevas}, Cerradas: {self.contador_preguntas_cerradas}")
        guardar_respuestas_sin_pregunta(self.mensajes_sueltos)

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

    def cerrar_pregunta(self, pregunta: Pregunta, mensaje: Mensaje, origen='sistema', motivo=None):
        pregunta.cerrar()
        self.preguntas_abiertas.remove(pregunta)
        self.preguntas_cerradas.append(pregunta)
        self.contador_preguntas_cerradas += 1
        logger_msj.debug(f"🟢 PREGUNTA CERRADA por {origen} ({motivo if motivo else mensaje.contenido})")
        guardar_pregunta_y_respuestas_en_log(pregunta, self.contador_preguntas_cerradas, self.nombre_log)

    def _asociar_o_registrar_suelto(self, mensaje: Mensaje):
        if self.preguntas_cerradas:
            for pregunta in self.preguntas_cerradas[-2:]:
                pregunta.agregar_respuesta(mensaje,lista_docentes)
                logger_msj.debug(f" 🔶 RESPUESTA TARDÍA: '{mensaje.contenido}' asociada a: '{pregunta.contenido}'")
        else:
            self.mensajes_sueltos.append(mensaje)
            logger_msj.debug(f" 🔴 MENSAJE SUELTO: '{mensaje.contenido}'")
