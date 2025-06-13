from dotenv import load_dotenv
import os
from utils_for_all.utilidades_logs import setup_logger

# Inicializar logger para esta parte del sistema
logger = setup_logger("conexion_bdd", "conexion_bdd.log")

# Cargar variables desde .env
load_dotenv()

# Obtener configuración desde variables de entorno (.env)
config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Validación con log
if not all(config.values()):
    logger.error("❌ Faltan variables de entorno para la conexión a la base de datos. Verificá el archivo .env.")
    raise ValueError("Faltan datos de conexión a la base de datos. Verificá el archivo .env")
else:
    logger.info("✅ Variables de entorno cargadas correctamente para la conexión a la base de datos.")
