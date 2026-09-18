from funciones_normalizadoras_de_texto import (
    normalizar_espacios_externos,
    normalizar_espacios_internos,
    convertir_a_minusculas
)
from normalizador_general_de_textos import NormalizadorTexto
from yaml_a_elementos_en_memoria import GestorYAML

class NormalizadorUsuariosDiscord:
    def __init__(self):
        # Configuramos el pipeline específico para usuarios (sin quitar símbolos)
        pipeline_usuarios = [
            normalizar_espacios_externos,
            normalizar_espacios_internos,
            convertir_a_minusculas
        ]
        # Le pasamos las funciones reales al inicializarlo
        self.normalizador_texto = NormalizadorTexto(pipeline=pipeline_usuarios)
        self.gestor_yaml = GestorYAML() # Tu gestor actual

    def normalizar_usuario(self, nombre_usuario: str) -> str:
        # Ahora la llamada es directa, limpia y sin errores de strings
        return self.normalizador_texto.aplicar_pipeline(nombre_usuario)
