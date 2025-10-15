from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta

class EstrategiaCierre:
    def cerrar(self, pregunta: Pregunta, mensaje: Mensaje, motivo: str):
        raise NotImplementedError("Debes implementar el método cerrar")

class EstrategiaCierreBatch(EstrategiaCierre):
    def __init__(self, procesador):
        self.procesador = procesador  # Para acceder a preguntas_abiertas, etc.

    def cerrar(self, pregunta: Pregunta, mensaje: Mensaje, motivo: str):
        pregunta.cerrar()
        self.procesador.registrar_cierre(pregunta, motivo)
            # self.procesador.preguntas_abiertas.remove(pregunta)
            # self.procesador.preguntas_cerradas.append(pregunta)
            # self.procesador.contador_preguntas_cerradas += 1
            #logger_msj.debug(f"🟢 PREGUNTA CERRADA por {motivo}")

class EstrategiaCierreTiempoReal(EstrategiaCierre):
    def cerrar(self, pregunta: Pregunta, mensaje: Mensaje, motivo: str):
        pregunta.esta_cerrada = True
        pregunta.save()  # Persistencia en base de datos
        #logger_msj.info(f"🔒 Pregunta {pregunta.id} cerrada por {motivo} en tiempo real")

