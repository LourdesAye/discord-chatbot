from database.models.clase_mensajes import Mensaje
from database.models.clase_preguntas import Pregunta
from utils.utilidades_logs import setup_logger, guardar_pregunta_y_respuestas_en_log
from database.utilidades_conversiones import convertir_a_datetime, tiempo_transcurrido
from datetime import timedelta
from database.estrategias_procesamiento import ProcesamientoAlumnoStrategy,ProcesamientoDocenteStrategy
from database.models.clase_autores import lista_docentes
from processing.estrategias_cierre_mensajes.estrategias_cierre_mensajes import EstrategiaCierreBatch
from processing.estrategias_cierre_mensajes.estrategias_cierre_mensajes import EstrategiaCierre
from abc import ABC, abstractmethod

logger_msj = setup_logger('procesamiento_de_mensajes', 'logs_procesar_mensajes.txt')
MAX_RESPUESTAS = 7
TIEMPO_CIERRE_HORAS = 8

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
            if pregunta.tiene_respuesta_validada(): # en tiempo real se debe tomar la pregunta con su id, buscarlo en la base de datos en la tabla respuestas, de las respuestas obtengo un id de usuario y por cada id de susuario hay que ir a al tabla autor para saber si es o no docente y por lo tanto si esta validada
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


    # va como método o va como atributo? 
    # @abstractmethod
    # def obtener_preguntas_abiertas(self) -> list[Pregunta]:
    #     pass

    # va como método o va como atributo?
    # @abstractmethod
    # def obtener_preguntas_cerradas(self) -> list[Pregunta]:
    #     pass


    # en tiempo real es distinto, se debe persistir la nueva prengunta en la base de datos relacional 
    # @abstractmethod
    # def guardar_pregunta(self, pregunta: Pregunta):
    #     pass

    # en batch es convertir el mensaje en un objeto Respuesta, 
    # ver si es de un docente para marcarla como validada, analizar si es corta para marcarla como tal, 
    # y agregarla a la lista de respuestas de la pregunta
    # en tiempo real necesito que se convierta en un objeto respuesta, para ver ver si es de docente
    # para marcarla como validada, ver si es corta para marcarla como tal, 
    # y también se necesita que se asociie a la pregunta pero con el id de la pregunta que se obtiene de la base de datos 
    # porque esta respuesta no queda en una lista, se debe persistir como mensaje y como respuesta en la base de datos con su id pregunta 
    # @abstractmethod
    # def guardar_respuesta(self, respuesta):
    #     pass

    # en el procesamiento batch cerrar_pregunta es marcar el objeto Pregunta como cerrrada, 
    # quitarla de la lista de preguntas abiertas
    # agregarla a la lista de preguntas cerradas y aumentar el contador de preguntas cerradas
    # y también hacer un log de que se cerró la pregunta
    # en tiempo real se debe marcar la pregunta como cerrada en la base de datos
    # @abstractmethod
    # def cerrar_pregunta(self, pregunta, mensaje, motivo):
    #     pass


class ProcesadorBatch(ProcesadorBase):
    # Extiende ProcesadorBase con atributos adicionales
    def __init__(self, nombre_log, estrategias=None):
        # Llama al constructor de la clase base
        super().__init__(nombre_log, estrategias) 
        # nuevos atributos específicos para batch
        self.mensajes_sueltos = []
        self.contador_mensajes = 0
        self.contador_preguntas_nuevas = 0
        self.contador_preguntas_cerradas = 0
        self.cant_concatenaciones = 0
        self.contador_mensaje_respuesta = 0
        self.cant_mens_cierre_alumnos = 0
        self.cant_mens_cierre_docente = 0
        self.estrategia_cierre = EstrategiaCierreBatch(self)  # se pasa self directamente para no hacer referencia circular 

    @property # para que se interprete como atributo y no como método ( self.preguntas_abiertas y no: self.preguntas_abiertas() )
    def preguntas_abiertas(self):
        return self._preguntas_abiertas

    def registrar_cierre(self, pregunta: Pregunta, motivo: str):
        self.preguntas_abiertas.remove(pregunta)
        self.preguntas_cerradas.append(pregunta)
        self.contador_preguntas_cerradas += 1
        logger_msj.debug(f"🟢 PREGUNTA CERRADA por {motivo}")

     # esto es lo que se esta borrando o cambiando 
    def procesar_dataframe(self, df, ruta_json):
        logger_msj.debug(" 🔵 Iniciando procesamiento del DataFrame...")
        for _, row in df.iterrows():
            mensaje = Mensaje.from_dataframe_row(row, ruta_json)
            self.contador_mensajes += 1
            logger_msj.debug(f" ... PROCESANDO MENSAJE {self.contador_mensajes}: '{mensaje.contenido}' ")
            self.procesar_mensaje(mensaje)
        logger_msj.debug("✅ PROCESAMIENTO FINALIZADO.")
        for numero_pregunta,pregunta in enumerate(self.preguntas_cerradas,start=1):
            guardar_pregunta_y_respuestas_en_log(pregunta, numero_pregunta,self.nombre_log)
        logger_msj.debug(f"Total mensajes: {self.contador_mensajes}, Preguntas nuevas: {self.contador_preguntas_nuevas}, Cerradas: {self.contador_preguntas_cerradas}")


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