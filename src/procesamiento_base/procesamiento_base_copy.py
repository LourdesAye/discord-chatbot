from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta
from utils_for_all.utilidades_logs import setup_logger, guardar_pregunta_y_respuestas_en_log
from database.knowledge_base.utils.utilidades_conversiones import convertir_a_datetime, tiempo_transcurrido
from datetime import timedelta
from database.knowledge_base.services.estrategias_procesamiento import ProcesamientoAlumnoStrategy,ProcesamientoDocenteStrategy
from database.knowledge_base.models.clase_autores import lista_docentes
from estrategias_cierre_mensajes.estrategias_de_cierre_de_menajes import EstrategiaCierre
from abc import ABC, abstractmethod

# ABC : Abstract Base Class (Clase Base Abstracta):  
    # Cuando tu clase hereda de ABC: 
        # no se puede instanciar la clase base directamente.
        # puede contener métodos abstractos (@abstractmethod) que no tienen implementación.
        # que las subclases deben implementar esos métodos abstractos antes de poder crearlas.

MAX_RESPUESTAS = 7
TIEMPO_CIERRE_HORAS = 8

class ProcesadorBase(ABC): # importante heredar de ABC
    def __init__(self, nombre_log, estrategias=None):
        """Constructor común para ambos procesadores (batch y tiempo real)."""
        self.nombre_log = nombre_log
        self.preguntas_abiertas = []
        self.preguntas_cerradas = []
        self.estrategias = estrategias or {
            'docente': ProcesamientoDocenteStrategy(),
            'alumno': ProcesamientoAlumnoStrategy()
        }
        self.estrategia_cierre = None # se define en las subclases
    
    @property # para que se interprete como atributo y no como método ( self.preguntas_abiertas y no: self.preguntas_abiertas() )
    @abstractmethod # obligaa definir este método en las subclases
    def preguntas_abiertas(self):
        pass # para que se implemente en las subclases
    
    def cerrar_pregunta(self, pregunta: Pregunta, mensaje: Mensaje, motivo=None):
        self.estrategia_cierre.cerrar(pregunta, mensaje, motivo) # FALTA CERRAR PREGUNTA PARA REAL TIME
    
    def cerrar_por_reglas(self, mensaje: Mensaje):
        ahora = convertir_a_datetime(mensaje.timestamp)
        for pregunta in self.preguntas_abiertas[:]: # en lo que es tiempo real la lista debe ser el resultado de una consulta a la base de datos de preguntas abiertas
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







   