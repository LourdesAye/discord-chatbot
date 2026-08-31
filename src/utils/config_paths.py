"""
Configuración del entorno del proyecto y de los directorios.
Utiliza pathlib para la gestión robusta de rutas y dotenv para el entorno.
"""
from pathlib import Path
from dotenv import load_dotenv
import os
from typing import List, Optional
from database.models.clase_ruta import Ruta


def buscar_archivo_en_padres(nombre_archivo: str, directorio_inicio: Optional[Path] = None) -> Path:
    """Busca un archivo recorriendo los directorios padres hacia arriba."""
    if directorio_inicio is None:
        try:
            directorio_inicio = Path(__file__).resolve().parent
        except NameError:
            directorio_inicio = Path.cwd()

    directorio_actual = directorio_inicio
    while True:
        ruta_candidata = directorio_actual / nombre_archivo
        if ruta_candidata.exists() and ruta_candidata.is_file():
            return ruta_candidata
        if directorio_actual.parent == directorio_actual:
            raise FileNotFoundError(
                f"❌ No se pudo encontrar {nombre_archivo} en ningún directorio padre de {directorio_inicio}"
            )
        directorio_actual = directorio_actual.parent


def configurar_entorno(nombre_archivo: str = ".env") -> Path:
    """Inicializa el entorno cargando las variables del .env y retorna la ruta raíz."""
    ruta_archivo_env = buscar_archivo_en_padres(nombre_archivo)
    load_dotenv(dotenv_path=ruta_archivo_env)
    return ruta_archivo_env.parent


CARPETA_PROYECTO = configurar_entorno()

LOG_DIR = os.getenv("LOG_DIR", "logs")
JSON_DIR = os.getenv("JSON_DIR", "json")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma")
DOCS_DIR = os.getenv("DOCS_DIR", "docs")

LOG_DIR_ABS = CARPETA_PROYECTO / LOG_DIR
JSON_DIR_ABS = CARPETA_PROYECTO / JSON_DIR
CHROMA_DIR_ABS = CARPETA_PROYECTO / CHROMA_DIR


class BuscadorArchivos:
    """Clase responsable de localizar y filtrar los archivos JSON en la estructura del proyecto."""

    def obtener_rutas_json(self, directorio_base: Optional[Path] = None) -> List[Ruta]:
        """Obtiene las rutas validadas de todos los archivos JSON encontrados."""
        directorio_base = directorio_base or JSON_DIR_ABS
        
        if not directorio_base.exists():
            raise FileNotFoundError(f"El directorio no existe: {directorio_base}")

        resultados: List[Ruta] = []
        patron_de_busqueda = os.getenv("FILE_NAME", "chat.json")
        profundidad_maxima = int(os.getenv("MAX_DEPTH", 999))

        # rglob ya busca recursivamente de forma nativa en pathlib
        for ruta_archivo in directorio_base.rglob(patron_de_busqueda):
            if not ruta_archivo.is_file():
                continue

            # Cálculo limpio usando propiedades nativas de pathlib
            ruta_relativa = ruta_archivo.relative_to(directorio_base)
            profundidad = len(ruta_relativa.parents)

            if profundidad <= profundidad_maxima:
                ruta_obj = Ruta(ruta_archivo)
                if ruta_obj.existe():
                    resultados.append(ruta_obj)

        return resultados