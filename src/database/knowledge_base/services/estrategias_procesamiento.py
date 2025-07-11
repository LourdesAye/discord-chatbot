from abc import ABC, abstractmethod # para crear clase abstracta y obligar a definir métodos a las clases hijas
from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta
from utils_for_all.utilidades_logs import setup_logger
from database.knowledge_base.models.clase_autores import lista_docentes

logger_msj = setup_logger('procesamiento_de_mensajes', 'logs_procesar_mensajes.txt')
logger_detectando_error = setup_logger('detectando_error','mistakes_detected.txt')
MAX_DELTA_SEGUNDOS_MSJ = 360

class ProcesamientoStrategy(ABC): # Hereda de ABC para ser una clase abstracta (que en este caso simula ser una interface)
    @abstractmethod # para marcar métodos que deben ser implementados obligatoriamente por las clases hijas.
    def procesar(self, procesador, mensaje: Mensaje): # os métodos abstractos no tienen implementación (solo firma)
        pass # Esto obliga a que las clases hijas implementen este método

class ProcesamientoDocenteStrategy(ProcesamientoStrategy): # ProcesamientoDocenteStrategy hereda de ProcesamientoStrategy
    def procesar(self, procesador, mensaje: Mensaje):
        if procesador.preguntas_abiertas:
            procesador.contador_mensaje_respuesta += 1
            for pregunta in procesador.preguntas_abiertas[:]:
                pregunta.agregar_respuesta(mensaje,lista_docentes)
                if mensaje.es_cierre_docente():
                    procesador.cerrar_pregunta(pregunta, mensaje, origen='docente')
                    procesador.cant_mens_cierre_docente += 1
        else:
            if procesador.preguntas_cerradas:
                procesador.contador_mensaje_respuesta += 1
                if len(procesador.preguntas_cerradas) == 1:
                    lista_unica_pregunta = procesador.preguntas_cerradas[-1:]
                    for pregunta in lista_unica_pregunta:
                        pregunta.agregar_respuesta(mensaje,lista_docentes)
                        logger_msj.debug(f" 🔶 RESPUESTA QUE LLEGA SIN PREGUNTAS ABIERTAS: '{mensaje.contenido}'")
                        logger_msj.debug(f" 🔶 SE ASOCIA A LA ULTIMA PREGUNTA CERRADA: '{pregunta.contenido}'")
                else: 
                    ultimas_dos = procesador.preguntas_cerradas[-2:]
                    for pregunta in ultimas_dos:
                        pregunta.agregar_respuesta(mensaje,lista_docentes)
                        logger_msj.debug(f" 🔶 RESPUESTA QUE LLEGA SIN PREGUNTAS ABIERTAS: '{mensaje.contenido}'")
                        logger_msj.debug(f" 🔶 SE ASOCIA A LA PREGUNTA CERRADA: '{pregunta.contenido}'")
            else:
                procesador.registrar_mensaje_suelto(mensaje)

class ProcesamientoAlumnoStrategy(ProcesamientoStrategy):# ProcesamientoAlumnoStrategy hereda de ProcesamientoStrategy
    def procesar(self, procesador, mensaje: Mensaje):
        if procesador.preguntas_abiertas:
            autores_abiertos = {p.autor for p in procesador.preguntas_abiertas}
            if mensaje.autor in autores_abiertos:
                for pregunta in procesador.preguntas_abiertas[:]:
                    if pregunta.tiene_mismo_autor(mensaje):
                        logger_detectando_error.debug(f"Mensaje:{mensaje.contenido} y Pregunta: {pregunta.contenido} poseen mismo autor")
                        if pregunta.es_extensible_con(mensaje, MAX_DELTA_SEGUNDOS_MSJ):
                            logger_detectando_error.debug(f"Es extensible la pregunta {pregunta.contenido} con el mensaje {mensaje.contenido}")
                            pregunta.concatenar_contenido(mensaje.contenido)
                            procesador.cant_concatenaciones += 1
                        elif mensaje.es_cierre_alumno() and pregunta.tiene_respuesta_validada():
                            procesador.cerrar_pregunta(pregunta, mensaje, origen='alumno')
                            procesador.cant_mens_cierre_alumnos += 1
                        else:
                            pregunta.agregar_respuesta(mensaje,lista_docentes)
                            procesador.contador_mensaje_respuesta += 1
            else:
                if mensaje.es_pregunta():
                    nueva = Pregunta(mensaje)
                    procesador.preguntas_abiertas.append(nueva)
                    procesador.contador_preguntas_nuevas += 1
                    logger_msj.debug(f"🟡 NUEVA PREGUNTA: {nueva.contenido}")
                else:
                    procesador.contador_mensaje_respuesta += 1
                    for preg in procesador.preguntas_abiertas[:]:
                        preg.agregar_respuesta(mensaje,lista_docentes)
        else:
            if mensaje.es_pregunta():
                nueva = Pregunta(mensaje)
                procesador.preguntas_abiertas.append(nueva)
                procesador.contador_preguntas_nuevas += 1
                logger_msj.debug(f"🟡 NUEVA PREGUNTA: {nueva.contenido}")
            else:
                if procesador.preguntas_cerradas:
                    procesador.contador_mensaje_respuesta +=1
                    if len(procesador.preguntas_cerradas)== 1:
                        lista_unica_pregunta = procesador.preguntas_cerradas[-1:]
                        for preg in lista_unica_pregunta:
                            preg.agregar_respuesta(mensaje,lista_docentes)
                    else:
                        ultimas_dos = procesador.preguntas_cerradas[-2:]
                        for preg in ultimas_dos:
                            preg.agregar_respuesta(mensaje,lista_docentes)
                else:
                    procesador.registrar_mensaje_suelto(mensaje)

# Strategy Pattern: para separar la lógica de procesamiento de mensajes por tipo de autor 
# Separación de responsabilidades: el Procesador delega tareas específicas, lo que facilita el mantenimiento y la extensión. 
# Reutilización de procesador.procesar_mensaje(mensaje) tanto con DataFrames como con mensajes individuales en tiempo real.
