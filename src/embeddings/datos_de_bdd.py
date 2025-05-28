import psycopg2
from psycopg2 import OperationalError, DatabaseError
from psycopg2.extras import DictCursor
from src.utils_for_all.conexion_bdd import config
from src.utils_for_all.utilidades_logs import setup_logger

logger_embeddings = setup_logger("logger_embeddings","logs_generacion_embeddings")

try:
    # Conexión a la base de datos con cursor tipo diccionario
    conn = psycopg2.connect(
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"]
    )
    cursor = conn.cursor(cursor_factory=DictCursor)

    # Ejecutar la consulta
    cursor.execute("""
        SELECT DISTINCT p.id_pregunta, p.texto
        FROM preguntas p
        JOIN respuestas r ON r.pregunta_id = p.id_pregunta
        WHERE r.es_validada = true
          AND (p.sin_contexto IS NULL OR p.sin_contexto = false)
          AND (p.es_administrativa IS NULL OR p.es_administrativa = false)
    """)

    # Obtener resultados
    resultados = cursor.fetchall()  # Lista de diccionarios

    # Separar en listas para LangChain
    preguntas = [fila["texto"] for fila in resultados]

    # Registrar preguntas en log 
    for indice,pregunta in enumerate(preguntas,start=1):
        logger_embeddings.debug(("═══════════════════════════════════════════════════════\n"))
        logger_embeddings.debug(f"PREGUNTA NÚMERO {indice}")
        logger_embeddings.debug(("═══════════════════════════════════════════════════════\n"))
        logger_embeddings.debug(f"{pregunta}")
        logger_embeddings.debug(f" ")
    
    metadatos = [{"id": fila["id"]} for fila in resultados]
# por si falla la conexión
except OperationalError as e:
    logger_embeddings.debug("Error de conexión a la base de datos:", e)
    preguntas = []
    metadatos = []

# por si hay un problema en la ejecución de la consulta
except DatabaseError as e:
    logger_embeddings.debug("Error al ejecutar la consulta:", e)
    preguntas = []
    metadatos = []

# asegura que se cierren la conexión y el cursor aunque ocurra un error.
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()