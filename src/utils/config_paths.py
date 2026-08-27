
"""
Configuración del entorno del proyecto y de los directorios.
Proporciona funciones para localizar archivos, cargar variables de entorno
y definir rutas absolutas de los directorios del proyecto.
También proporciona métodos para buscar archivos JSON.
"""

from pathlib import Path
from dotenv import load_dotenv
import os
from typing import List, Optional
from database.models.clase_ruta import Ruta


def buscar_archivo_en_padres(nombre_archivo: str, directorio_inicio: Optional[Path] = None) -> Path:
    """
    Busca un archivo recorriendo los directorios padres.

    Args:
        nombre_archivo (str): Nombre del archivo a buscar.
        directorio_inicio (Path, opcional): Directorio desde el cual comenzar la búsqueda.
            Si no se especifica, utiliza la ubicación del script o el
            directorio de trabajo actual.

    Returns:
        Path: Ruta completa del archivo encontrado.

    Raises:
        FileNotFoundError: Si el archivo no se encuentra en ningún directorio padre.
    """
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
                f" ❌ No se pudo encontrar {nombre_archivo} en ningún directorio padre de {directorio_inicio}"
            )
        directorio_actual = directorio_actual.parent


def configurar_entorno(nombre_archivo: str = ".env") -> Path:
    """
    Inicializa el entorno del proyecto cargando las variables definidas
    en un archivo .env.

    Args:
        nombre_archivo (str, opcional): Nombre del archivo de variables de entorno.
            Por defecto es ".env".

    Returns:
        Path: Directorio raíz del proyecto (directorio padre del archivo .env).

    Raises:
        FileNotFoundError: Si el archivo .env no se encuentra en ningún
            directorio padre.
    """
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


def obtener_archivos_por_patron(directorio_base: Path, patron_busqueda: str) -> List[Path]:
    """
    Busca todos los archivos dentro de un directorio y sus subdirectorios
    que coincidan con un patrón de búsqueda.

    Args:
        directorio_base (Path): Directorio donde realizar la búsqueda.
        patron_busqueda (str): Patrón que deben cumplir los nombres de los archivos.

    Returns:
        List[Path]: Lista de rutas de los archivos encontrados.
    """
    return list(directorio_base.rglob(patron_busqueda))


def es_archivo_regular(archivo: Path) -> bool:
    """
    Verifica si la ruta corresponde a un archivo regular
    (no un directorio ni un enlace simbólico).

    Args:
        archivo (Path): Ruta a verificar.

    Returns:
        bool: True si es un archivo regular; False en caso contrario.
    """
    return archivo.is_file()


def obtener_ruta_relativa(archivo: Path, directorio_base: Path) -> Path:
    """
    Obtiene la ruta relativa de un archivo respecto del directorio base.

    Args:
        archivo (Path): Ruta del archivo.
        directorio_base (Path): Directorio base desde el cual calcular la ruta relativa.

    Returns:
        Path: Ruta relativa del archivo.
    """
    return archivo.relative_to(directorio_base)


def calcular_profundidad(ruta_relativa: Path) -> int:
    """
    Calcula la profundidad de una ruta relativa.

    La profundidad corresponde a la cantidad de directorios que separan
    el archivo del directorio base.

    Args:
        ruta_relativa (Path): Ruta relativa cuya profundidad se desea calcular.

    Returns:
        int: Profundidad de la ruta.
    """
    return len(ruta_relativa.parents)


class BuscadorArchivos:
    """
    Clase que permite buscar archivos dentro de la estructura del proyecto.
    """

    def obtener_rutas_json(self, directorio_base: Path = None) -> List[Ruta]:
        """
        Obtiene las rutas de todos los archivos JSON encontrados dentro
        del directorio especificado.

        Args:
            directorio_base (Path, opcional): Directorio base donde buscar los
                archivos JSON. Si no se especifica, se utiliza JSON_DIR_ABS.

        Returns:
            List[Ruta]: Lista de objetos Ruta correspondientes a los archivos encontrados.

        Raises:
            FileNotFoundError: Si el directorio base no existe.
        """
        directorio_base = directorio_base or JSON_DIR_ABS
        if not directorio_base.exists():
            raise FileNotFoundError(f"El directorio no existe: {directorio_base}")

        resultados: List[Ruta] = []
        patron_de_busqueda = os.getenv("FILE_NAME", "chat.json")
        profundidad_maxima = int(os.getenv("MAX_DEPTH", 999))

        lista_rutas_archivos = obtener_archivos_por_patron(directorio_base, patron_de_busqueda)

        for ruta_archivo in lista_rutas_archivos:
            if not es_archivo_regular(ruta_archivo):
                continue

            ruta_relativa = obtener_ruta_relativa(ruta_archivo, directorio_base)
            profundidad = calcular_profundidad(ruta_relativa)

            if profundidad <= profundidad_maxima:
                ruta_obj = Ruta(ruta_archivo)
                if ruta_obj.existe():
                    resultados.append(ruta_obj)

        return resultados
