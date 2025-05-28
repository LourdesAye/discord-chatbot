from src.utils_for_all.utilidades_logs import setup_logger

logger_proc= setup_logger('carga_procesador','log_procesamiento_con_preguntas_cerradas.txt')

class AnalizadorPreguntasCerradas:
    def __init__(self, preguntas):
        self.cant_preg_sin_contexto =0 
        self.cant_preg_cerradas = 0
        self.cant_respuestas = 0
        self.preguntas=preguntas

    def marcar_preguntas_sin_contexto(self):
        for pregunta in self.preguntas:
            pregunta.marcar_sin_contexto()
        return self.preguntas

    def agregar_es_administrativa (self,preguntas_a_marcar):
        for pregunta in preguntas_a_marcar:
            pregunta.marcar_administrativa()
        return preguntas_a_marcar

    def marcar_respuestas_cortas(self,preguntas_a_marcar):
        for pregunta in preguntas_a_marcar:
            for respuesta in pregunta.respuestas:
                respuesta.marcar_como_corta()
        return preguntas_a_marcar
    
    # necesito que devuelva : total de respuestas, total de preguntas, preguntas_a_procesar
    def aplicar_analisis_preguntas(self,num_procesador):

        logger_proc.debug(f" ")
        logger_proc.debug(f" 🔢 Analizando el json número : {num_procesador} ... ")
        logger_proc.debug(f" ✅ Preguntas cerradas: {len(self.preguntas)} ")

        preguntas_con_contexto = self.marcar_preguntas_sin_contexto()
        for pregunta in preguntas_con_contexto:
            if pregunta.sin_contexto:
                self.cant_preg_sin_contexto=self.cant_preg_sin_contexto +1

        logger_proc.debug(f" ✅ Preguntas sin contexto: {self.cant_preg_sin_contexto} ")

        preguntas_con_estado = self.agregar_es_administrativa (preguntas_con_contexto)
        preguntas_marcadas_respuestas_cortas = self.marcar_respuestas_cortas(preguntas_con_estado)

        total_reg_preguntas= len(preguntas_marcadas_respuestas_cortas) # cantidad de preguntas cerradas en cada procesamiento de archivo
        
        for index,pregunta in enumerate(preguntas_marcadas_respuestas_cortas,start=1): # se van acumulando la cantidad de respuestas totales
            self.cant_respuestas = self.cant_respuestas +len(pregunta.respuestas)
        
        logger_proc.debug(f" ✅ Cantidad de Respuestas: {self.cant_respuestas}")
        return total_reg_preguntas, self.cant_respuestas, preguntas_marcadas_respuestas_cortas