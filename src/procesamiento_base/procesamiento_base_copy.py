from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta
from utils_for_all.utilidades_logs import setup_logger, guardar_pregunta_y_respuestas_en_log
from database.knowledge_base.utils.utilidades_conversiones import convertir_a_datetime, tiempo_transcurrido
from datetime import timedelta
from database.knowledge_base.services.estrategias_procesamiento import ProcesamientoAlumnoStrategy,ProcesamientoDocenteStrategy
from database.knowledge_base.models.clase_autores import lista_docentes
from estrategias_cierre_mensajes.estrategias_cierre_menajes import EstrategiaCierre

MAX_RESPUESTAS = 7
TIEMPO_CIERRE_HORAS = 8

class ProcesadorBase:
    def __init__(self, nombre_log, estrategia_cierre: EstrategiaCierre,  estrategias=None):
        """Constructor común para ambos procesadores (batch y tiempo real)."""
        self.nombre_log = nombre_log
        self.preguntas_abiertas = []
        self.preguntas_cerradas = []
        self.estrategias = estrategias or {
            'docente': ProcesamientoDocenteStrategy(),
            'alumno': ProcesamientoAlumnoStrategy()
        }
        self.estrategia_cierre = estrategia_cierre
    
    def cerrar_pregunta(self, pregunta: Pregunta, mensaje: Mensaje, motivo=None):
        self.estrategia_cierre.cerrar(pregunta, mensaje, motivo) # FALTA CERRAR PREGUNTA PARA REAL TIME
    
    def cerrar_por_reglas(self, mensaje: Mensaje):
        ahora = convertir_a_datetime(mensaje.timestamp)
        for pregunta in self.preguntas_abiertas[:]:
            tiempo = tiempo_transcurrido(convertir_a_datetime(pregunta.timestamp), ahora)
            if pregunta.tiene_respuesta_validada():
                if tiempo > timedelta(hours=TIEMPO_CIERRE_HORAS):
                    self.cerrar_pregunta(pregunta, mensaje, motivo='tiempo')
                elif len(pregunta.respuestas) >= MAX_RESPUESTAS:
                    self.cerrar_pregunta(pregunta, mensaje, motivo='cantidad')


    # Se procesa un único mensaje (común para batch y tiempo real)
    def procesar_mensaje(self, mensaje: Mensaje):
        """Maneja la clasificación de un único mensaje (común para batch y tiempo real)."""

        # primero aplicar reglas de cierre (basadas en tiempo/cantidad)
        self.cerrar_por_reglas(mensaje)

        # delegar a la estrategia según tipo de autor
        tipo = 'docente' if mensaje.es_autor_docente() else 'alumno'
        self.estrategias[tipo].procesar(self, mensaje)







   