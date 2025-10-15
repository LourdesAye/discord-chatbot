from procesamiento_base.procesamiento_base_copy import ProcesadorBase
from estrategias_cierre_mensajes.estrategias_de_cierre_de_menajes import EstrategiaCierreTiempoReal

class ProcesadorTiempoReal(ProcesadorBase):
    # definición explícita solo por claridad del constructor aunque no hace falta
    def __init__(self, nombre_log, estrategias=None):
        # mismos atributos que clase base
        super().__init__(nombre_log, estrategias)
        self.estrategia_cierre = EstrategiaCierreTiempoReal()  # estrategia de cierre para tiempo real

    @property # para que se interprete como atributo y no como método ( self.preguntas_abiertas y no: self.preguntas_abiertas() )
    def preguntas_abiertas(self):
        """Consulta dinámica a la base de datos."""
        return ["Pendiente de implementar"] # debe ser una consulta a la base de datos
        #return Pregunta.obtener_preguntas_abiertas()
    