
import clase_respuestas
import clase_preguntas
from utilidades.utilidades_logs import setup_logger

logger_proc= setup_logger('carga_procesador','log_carga_de_procesador_con_preguntas_cerradas.txt')

class AnalizadorPreguntasCerradas:
    def __init__(self, preguntas):
        self.cant_preg_sin_contexto =0 
        self.cant_preg_cerradas = 0
        self.cant_respuestas = 0

    def marcar_preguntas_sin_contexto(preguntas):
        for pregunta in preguntas:
            pregunta.marcar_sin_contexto()
        return preguntas

    def agregar_es_administrativa (preguntas):
        for pregunta in preguntas:
            pregunta.marcar_administrativa()
        return preguntas

    def marcar_respuestas_cortas(preguntas):
        for pregunta in preguntas:
            for respuesta in pregunta.respuestas:
                respuesta.marcar_como_corta()
        return preguntas
    
    # necesito que devuelva : total de respuestas, total de preguntas, preguntas_a_procesar
    def aplicar_analisis_preguntas(self,num_procesador):
        
        logger_proc.debug(f"Preguntas cerradas: {len(self.preguntas)} ")

        preguntas_con_contexto = self.marcar_preguntas_sin_contexto(self.preguntas)
        for pregunta in preguntas_con_contexto:
            if pregunta.sin_contexto:
                self.cant_preg_sin_contexto=self.cant_preg_sin_contexto +1

        logger_proc.debug(f"Preguntas sin contexto detectadas: {self.cont_preg_sin_contexto} ")

        preguntas_con_estado = self.agregar_es_administrativa (preguntas_con_contexto)
        preguntas_marcadas_respuestas_cortas = self.marcar_respuestas_cortas(preguntas_con_estado)

        total_reg_preguntas= len(preguntas_marcadas_respuestas_cortas) # cantidad de preguntas cerradas en cada procesamiento de archivo
        
        logger_proc.debug(f" ")
        logger_proc.debug(f"analizando el json número : {num_procesador}")
        logger_proc.debug(f"Cantidad de Preguntas Cerradas {len(preguntas_marcadas_respuestas_cortas)}")
        for index,pregunta in enumerate(preguntas_marcadas_respuestas_cortas,start=1): # se van acumulando la cantidad de respuestas totales
            cant_resp=cant_resp+len(pregunta.respuestas)
        
        return total_reg_preguntas, cant_resp, preguntas_marcadas_respuestas_cortas