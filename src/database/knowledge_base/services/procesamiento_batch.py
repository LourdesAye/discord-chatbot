from procesamiento_base.procesamiento_base_copy import ProcesadorBase
from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta
from utils_for_all.utilidades_logs import setup_logger, guardar_pregunta_y_respuestas_en_log
from database.knowledge_base.utils.utilidades_conversiones import convertir_a_datetime, tiempo_transcurrido
from datetime import timedelta
from database.knowledge_base.services.estrategias_procesamiento import ProcesamientoAlumnoStrategy,ProcesamientoDocenteStrategy
from database.knowledge_base.models.clase_autores import lista_docentes
from estrategias_cierre_mensajes.estrategias_cierre_menajes import EstrategiaCierreBatch

logger_msj = setup_logger('procesamiento_de_mensajes', 'logs_procesar_mensajes.txt')
MAX_RESPUESTAS = 7
TIEMPO_CIERRE_HORAS = 8


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

    def registrar_cierre(self, pregunta: Pregunta, motivo: str):
        self.preguntas_abiertas.remove(pregunta)
        self.preguntas_cerradas.append(pregunta)
        self.contador_preguntas_cerradas += 1
        logger_msj.debug(f"🟢 PREGUNTA CERRADA por {motivo}")

     # esto es lo que se esta borrando o cambiando 
    # def procesar_dataframe(self, df, ruta_json):
    #     logger_msj.debug(" 🔵 Iniciando procesamiento del DataFrame...")
    #     for _, row in df.iterrows():
    #         mensaje = Mensaje.from_dataframe_row(row, ruta_json)
    #         self.contador_mensajes += 1
    #         logger_msj.debug(f" ... PROCESANDO MENSAJE {self.contador_mensajes}: '{mensaje.contenido}' ")
    #         self.cerrar_por_reglas(mensaje)
    #         self.procesar_mensaje(mensaje)
    #     logger_msj.debug("✅ PROCESAMIENTO FINALIZADO.")
    #     for numero_pregunta,pregunta in enumerate(self.preguntas_cerradas,start=1):
    #         guardar_pregunta_y_respuestas_en_log(pregunta, numero_pregunta,self.nombre_log)
    #     logger_msj.debug(f"Total mensajes: {self.contador_mensajes}, Preguntas nuevas: {self.contador_preguntas_nuevas}, Cerradas: {self.contador_preguntas_cerradas}")


    # def cerrar_pregunta(self, pregunta: Pregunta, mensaje: Mensaje, motivo=None):
    #     pregunta.cerrar()
    #     self.preguntas_abiertas.remove(pregunta)
    #     self.preguntas_cerradas.append(pregunta)
    #     self.contador_preguntas_cerradas += 1
    #     logger_msj.debug(f"🟢 PREGUNTA CERRADA por {motivo}")

    # def registrar_mensaje_suelto(self, mensaje: Mensaje):
    #         self.mensajes_sueltos.append(mensaje)
    #         autor_tipo = "DOCENTE" if mensaje.es_autor_docente() else "ALUMNO"
    #         logger_msj.debug(f" 🔴 MENSAJE SUELTO: '{mensaje.contenido}' de {autor_tipo} : {mensaje.autor} ")

    # def asociar_respuesta_a_preguntas_cerradas(self, mensaje, lista_docentes):
    #     self.contador_mensaje_respuesta += 1
    #     cantidad = len(self.preguntas_cerradas)
    #     preguntas_a_asociar = (
    #         self.preguntas_cerradas[-1:]
    #         if cantidad == 1
    #         else self.preguntas_cerradas[-2:]
    #     )
    #     for pregunta in preguntas_a_asociar:
    #         pregunta.agregar_respuesta(mensaje, lista_docentes)
    #         logger_msj.debug(f" 🔶 RESPUESTA QUE LLEGA SIN PREGUNTAS ABIERTAS: '{mensaje.contenido}'")
    #         logger_msj.debug(f" 🔶 SE ASOCIA A LA PREGUNTA CERRADA: '{pregunta.contenido}'")
