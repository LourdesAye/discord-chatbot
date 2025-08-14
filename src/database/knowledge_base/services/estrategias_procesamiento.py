from abc import ABC, abstractmethod # para crear clase abstracta y obligar a definir métodos a las clases hijas
from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta
from utils_for_all.utilidades_logs import setup_logger
from database.knowledge_base.models.clase_autores import lista_docentes

logger_msj = setup_logger('procesamiento_de_mensajes', 'logs_procesar_mensajes.txt')
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
                logger_msj.debug(f" ✅️ Se ha agregado una nueva respuesta : {mensaje.contenido}")
                if mensaje.es_cierre_docente():
                    procesador.cerrar_pregunta(pregunta, mensaje, motivo='docente')
                    procesador.cant_mens_cierre_docente += 1
        else:
            if procesador.preguntas_cerradas:
                procesador.asociar_respuesta_a_preguntas_cerradas(mensaje,lista_docentes)
            else:
                procesador.registrar_mensaje_suelto(mensaje)

class ProcesamientoAlumnoStrategy(ProcesamientoStrategy):# ProcesamientoAlumnoStrategy hereda de ProcesamientoStrategy
    def procesar(self, procesador, mensaje: Mensaje):
        if procesador.preguntas_abiertas:
            autores_abiertos = {p.autor for p in procesador.preguntas_abiertas}
            if mensaje.autor in autores_abiertos:
                for pregunta in procesador.preguntas_abiertas[:]:
                    if pregunta.tiene_mismo_autor(mensaje):
                        if pregunta.es_extensible_con(mensaje, MAX_DELTA_SEGUNDOS_MSJ):
                            pregunta.concatenar_contenido(mensaje.contenido)
                            logger_msj.debug(f" 📌 Se concatenó la pregunta: \n {pregunta.contenido} \n con el mensaje: {mensaje.contenido}")
                            procesador.cant_concatenaciones += 1
                        elif mensaje.es_cierre_alumno() and pregunta.tiene_respuesta_validada():
                            procesador.cerrar_pregunta(pregunta, mensaje, motivo='alumno')
                            procesador.cant_mens_cierre_alumnos += 1
                        else:
                            pregunta.agregar_respuesta(mensaje,lista_docentes)
                            logger_msj.debug(f" ✅️ Se ha agregado una nueva respuesta : {mensaje.contenido}")
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
                        logger_msj.debug(f" ✅️ Se ha agregado una nueva respuesta : {mensaje.contenido}")
        else:
            if mensaje.es_pregunta():
                nueva = Pregunta(mensaje)
                procesador.preguntas_abiertas.append(nueva)
                procesador.contador_preguntas_nuevas += 1
                logger_msj.debug(f"🟡 NUEVA PREGUNTA: {nueva.contenido}")
            else:
                if procesador.preguntas_cerradas:
                    procesador.asociar_respuesta_a_preguntas_cerradas(mensaje,lista_docentes)
                else:
                    procesador.registrar_mensaje_suelto(mensaje)

# Strategy Pattern: para separar la lógica de procesamiento de mensajes por tipo de autor 
# Separación de responsabilidades: el Procesador delega tareas específicas, lo que facilita el mantenimiento y la extensión. 
# Reutilización de procesador.procesar_mensaje(mensaje) tanto con DataFrames como con mensajes individuales en tiempo real.
