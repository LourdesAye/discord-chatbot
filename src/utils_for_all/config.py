from pathlib import Path
from dotenv import load_dotenv
import os

# NOTA:
# si __file__ es /home/usuario/proyecto/app/config.py, entonces: 
# Path(__file__).resolve().parent es /home/usuario/proyecto/app

# __file__ : ruta completa incluyendo el archivo que se está ejecutando.
# Path: la convierte en un objeto Path, 
# resolve() la convierte en una ruta absoluta.
# .parent → Devuelve el directorio contenedor del archivo.

# current = Path("/home/usuario/proyecto")
# filename = ".env"
# target = current / filename  # → Path("/home/usuario/proyecto/.env")

# current = Path("/home/usuario/proyecto/app")
# current = current.parent  # ahora es Path("/home/usuario/proyecto")

 # raise: lanza una excepción. Detiene el programa y muestra el mensaje de error si el archivo no se encuentra.

# Busca un archivo hacia arriba en la jerarquía de carpetas desde start_dir o desde el script actual.
# por defecto start_dir es None y str es tipo cadena de texto

def get_ruta_archivo(nombre_archivo: str, directorio_inicial: Path = None) -> Path:
    if directorio_inicial is None:
        directorio_inicial = Path(__file__).resolve().parent  # agarra el directorio que contiene al archivo actual
    directorio_actual = directorio_inicial
    while True:
        posible_ruta_env = directorio_actual / nombre_archivo # concatena mediante la barra las rutas que están en cada variable
        if posible_ruta_env.exists(): # si existe la ruta del archivo .env 
            return posible_ruta_env # se devuelve esa ruta que es la del archivo .env
        if directorio_actual.parent == directorio_actual: # quiere decir que se llegó al directorio raíz del equipo sin encontrar el .env
            raise FileNotFoundError(f"No se encontró {nombre_archivo} en ningún directorio superior a {directorio_inicial}")
        directorio_actual = directorio_actual.parent # se cambia al directorio padre del directorio actual para seguir con el analisis en la siguiente iteración

def cargar_ruta_env(nombre_archivo: str = ".env"): # flineame: str significa que es cadena de texto y que su valor por defecto es ".env"
    env_path = get_ruta_archivo(nombre_archivo) 
    load_dotenv(dotenv_path=env_path) # Busca un archivo .env en el disco (en este caso, en env_path). Carga las variables definidas ahí.
    return env_path.parent  # Devuelve el directorio en el que esta el archivo .env (sería el directorio raíz del proyecto)

# ==== CARGA DE ENTORNO ====
PROJECT_ROOT = cargar_ruta_env()

# ==== VARIABLES DE CONFIGURACIÓN ====
# gtetenv : Busca y devuelve si existe una variable de entorno con el nombre que se le pasa. 
# Si no existe, devuelve el segundo argumento (el valor por defecto).
LOG_DIR = os.getenv("LOG_DIR", "logs")
JSON_DIR = os.getenv("JSON_DIR", "json")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma")
DOCS_DIR = os.getenv("DOCS_DIR", "docs")

# Rutas absolutas
# usar rutas absolutas evita errores cuando estás en diferentes carpetas o entornos.
LOG_DIR_ABS = PROJECT_ROOT / LOG_DIR
JSON_DIR_ABS = PROJECT_ROOT / JSON_DIR
CHROMA_DIR_ABS = PROJECT_ROOT / CHROMA_DIR
DOCS_DIR_ABS = PROJECT_ROOT / DOCS_DIR