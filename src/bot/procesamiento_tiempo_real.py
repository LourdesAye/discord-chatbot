from procesamiento_base.procesamiento_base_copy import ProcesadorBase

class ProcesadorTiempoReal(ProcesadorBase):
    # definición explícita solo por claridad del constructor aunque no hace falta
    def __init__(self, nombre_log, estrategias=None):
        # mismos atributos que clase base
        super().__init__(nombre_log, estrategias)

    