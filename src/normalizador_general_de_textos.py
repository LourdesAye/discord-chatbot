"""
Recibe una lista de funciones (callables) y las aplica en cascada
- no usa getattr ni depende de nombres de texto, evitando riesgo de tipos: 
    - si se escribe mal el nombre de una función,el editor de código o IDE avisará inmediatamente con un error de importación
    - Con getattr y strings, el error salta recién al ejecutar el programa.
- flexibilidad: si se usara una función de una librería externa (o una función lambda rápida), se puede meter en la lista directamente sin tener que modificar la clase NormalizadorTexto.
"""

from typing import Callable

# alias para que el código sea más legible: una función que recibe str y devuelve str
FuncionNormalizadora = Callable[[str], str]

class NormalizadorTexto:
    def __init__(self, pipeline: list[FuncionNormalizadora]):
        """Recibe una lista de funciones en el orden que se deben ejecutar."""
        self.pipeline = pipeline

    def aplicar_pipeline(self, texto: str) -> str:
        """Aplica cada función del pipeline al texto de forma secuencial."""
        for funcion in self.pipeline:
            texto = funcion(texto)
        return texto

