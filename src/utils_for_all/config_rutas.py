from pathlib import Path # para manejar rutas de forma segura (mejor que strings).
from dotenv import load_dotenv # función que cargar variables de entorno desde un archivo .env en Python
import os #  interactuar con el sistema operativo( manipular archivos y directorios, entre otros.) 
from typing import List, Tuple # para la anotación de tipos y así mejorar la legibilidad del código y la detección de errores
from database.knowledge_base.models.clase_ruta import Ruta
from utilidades_logs import setup_logger

# ============= log para trazabilidad de la obtención de rutas o directorios ========== # 
logger_admin_rutas = setup_logger("admin_rutas","rutas_utilizadas.txt")

# ======================= FUNCIÓN que busca un ARCHIVO ================================ # 
# busca un archivo específico (por ejemplo, .env) recorriendo hacia arriba la jerarquía de directorios, 
# comenzando desde un directorio dado (o desde el directorio del archivo actual si no se especifica uno). 
def get_ruta_completa_archivo(nombre_archivo: str, directorio_inicial: Path = None) -> Path:
    logger_admin_rutas.debug("")
    logger_admin_rutas.debug(f" 📂 Se va a buscar la ruta del archivo: {nombre_archivo}")
    if directorio_inicial is None:
        directorio_inicial = Path(__file__).resolve().parent  # agarra el directorio (parent) que contiene al archivo actual(__file__)
    directorio_actual = directorio_inicial
    logger_admin_rutas.debug(f" 1️⃣ El directorio inicial es: {directorio_actual}")
    while True:
        posible_ruta_env = directorio_actual / nombre_archivo # concatena mediante la barra las rutas que están en cada variable
        if posible_ruta_env.exists(): # si existe la ruta del archivo .env 
            logger_admin_rutas.debug(f" ✅ Se encontro el archivo .env en esta ruta : {posible_ruta_env}")
            return posible_ruta_env # se devuelve esa ruta que es la del archivo .env
        if directorio_actual.parent == directorio_actual: # quiere decir que se llegó al directorio raíz del equipo sin encontrar el .env
            raise FileNotFoundError(f" ❌ No se encontró {nombre_archivo} en ningún directorio superior a {directorio_inicial}") # lanza una excepción. Detiene el programa y muestra el mensaje de error si el archivo no se encuentra.
        directorio_actual = directorio_actual.parent # se cambia al directorio padre del directorio actual para seguir con el analisis en la siguiente iteración
        logger_admin_rutas.debug(f" 🔄 El nuevo directorio actual es:{directorio_actual}")

# ================= FUNCIÓN que obtiene el DIRECTORIO que contiene a cierto ARCHIVO =================== # 
def cargar_ruta_directorio_archivo(nombre_archivo: str = ".env"): # flineame: str significa que es cadena de texto y que su valor por defecto es ".env"
    env_path = get_ruta_completa_archivo(nombre_archivo) 
    load_dotenv(dotenv_path=env_path) # Busca un archivo .env en el disco (en este caso, en env_path). Carga las variables definidas ahí.
    logger_admin_rutas.debug(f" 📂 La ruta del proyecto es: {env_path.parent}")
    return env_path.parent  # Devuelve el directorio en el que esta el archivo .env (sería el directorio raíz del proyecto)

# ===================== CARGA DE VARIABLES DE ENTORNO ========================== #
logger_admin_rutas.debug(" 📂 Se van a cargar las rutas desde el archivo .env")
# por defecto carga la ruta del directorio raíz del proyecto
PROJECT_ROOT = cargar_ruta_directorio_archivo()
logger_admin_rutas.debug(" ✅ Directorio raíz del proyecto: ", PROJECT_ROOT)

# Nombres de Directorios (solo nombres, no rutas) en el proyecto
LOG_DIR = os.getenv("LOG_DIR", "logs") # gtetenv : Busca y devuelve si existe una variable de entorno con el nombre que se le pasa. Si no existe, devuelve el segundo argumento (el valor por defecto).
JSON_DIR = os.getenv("JSON_DIR", "json")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma")
DOCS_DIR = os.getenv("DOCS_DIR", "docs")

# Generación de Rutas absolutas (necesaria para evitar errores al estar manejando varios archivos)
# Concatenando el directorio raíz del proyecto con el nombre de cada carpeta se da lugar a la ruta absoluta
LOG_DIR_ABS = PROJECT_ROOT / LOG_DIR
logger_admin_rutas.debug(f" ✅ Directorio de los logs del proyecto: {LOG_DIR_ABS}")
JSON_DIR_ABS = PROJECT_ROOT / JSON_DIR
logger_admin_rutas.debug(f" ✅ Directorio de los archivos JSON del proyecto: {LOG_DIR_ABS}")
CHROMA_DIR_ABS = PROJECT_ROOT / CHROMA_DIR
logger_admin_rutas.debug(f" ✅ Directorio de los embeddings {CHROMA_DIR_ABS}")


class BuscadorArchivos:
    def __init__(self): # método especial llamado automáticamente cuando se crea una nueva instancia de una clase (inicialización)
        self._criterios_busqueda = { # _diccionario : convención para indicar que es para uso interno dentro del módulo, clase o paquete donde se define
            "json": { # diccionario
                "nombre_archivo": "chat.json", # Archivo a buscar
                "profundidad_maxima": 4  # Para evitar búsquedas muy profundas (Ajustar si cambia la estructura de carpetas)
            },
            "imagenes": { # diccionario
                "nombre_directorio": "images",  # Carpeta a buscar
                "profundidad_maxima": 4 # Máximo de subcarpetas a explorar (Ajustar si cambia la estructura de carpetas)
            }
        }

    # Busca automáticamente archivos JSON y directorios de imágenes.
    def encontrar_archivos(self, directorio_base: Path = None) -> Tuple[List[Ruta], List[Ruta]]: # lista_rutas_json, lista_rutas_imagenes

        directorio_base = directorio_base or JSON_DIR_ABS
        logger_admin_rutas.debug(f"🔍 Iniciando búsqueda en: {directorio_base}")

        if not directorio_base.exists():
            raise FileNotFoundError(f"Directorio base no existe: {directorio_base}")

        rutas_json = self._buscar_archivos( # _: convención para indicar que es para uso interno dentro del módulo, clase o paquete donde se define
            directorio_base, 
            self._criterios_busqueda["json"] # devuelve un diccionario
        )
        
        rutas_imagen = self._buscar_directorios(
            directorio_base,
            self._criterios_busqueda["imagenes"]  # devuelve un diccionario
        )

        logger_admin_rutas.debug(f"✅ Encontrados {len(rutas_json)} JSON y {len(rutas_imagen)} directorios de imágenes")
        return rutas_json, rutas_imagen # devuelve una tupla con dos listas: rutas de JSONs y rutas de imágenes.

    # directorio es la ruta absoluta, criterios son los nombres de carpetas o directorios a buscar
    def _buscar_archivos(self, directorio: Path, criterios: dict) -> List[Ruta]:
        encontrados = []
        for archivo in directorio.rglob(criterios["nombre_archivo"]): # busca en el directorio actual y todos sus subdirectorios los archivos llamados chat.json. 
            # a partir de la ruta archivo se obtine la ruta relativa al directorio base (o sea que se quita el directorio base de la ruta archivo y esa es la ruta relativa)
            profundidad = len(archivo.relative_to(directorio).parents) # devuelve cantidad de padres (directorios) de la ruta relativa. 
            if profundidad <= criterios["profundidad_maxima"]:
                ruta_objeto = Ruta(archivo)
                if ruta_objeto.existe(): # verifica si existe esa ruta
                    encontrados.append(ruta_objeto) # agregra ruta a la lista
                    logger_admin_rutas.debug(f"📄 JSON encontrado: {ruta_objeto.__str__}")
        return encontrados

    def _buscar_directorios(self, directorio: Path, criterios: dict) -> List[Ruta]:
        encontrados = []
        for dir_imagen in directorio.rglob(criterios["nombre_directorio"]):# busca en el directorio actual y todos sus subdirectorios los directorios llamados images. 
            # a partir de la ruta dir_imagen se obtine la ruta relativa al directorio base (o sea que se quita el directorio base de la ruta dir_imagen y esa es la ruta relativa)
            profundidad = len(dir_imagen.relative_to(directorio).parents) # devuelve cantidad de padres (directorios) de la ruta relativa.
            if profundidad <= criterios["profundidad_maxima"] and dir_imagen.is_dir(): # is_dir : Verifica que el elemento sea un directorio (no un archivo)
                ruta_objeto = Ruta(dir_imagen) 
                encontrados.append(ruta_objeto) # no verifica existencia porque ya se valida antes con is_dir
                logger_admin_rutas.debug(f"🖼️ Directorio de imágenes: {ruta_objeto.__str__}")
        return encontrados
