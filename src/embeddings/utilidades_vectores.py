import shutil
import os
from utils_for_all.utilidades_logs import setup_logger

# por ahora conviven dos logs : el primero para responder_a_pregunta, y el segundo para probar_busqueda
logger_embeddings = setup_logger("logger_embeddings", "logs_generacion_embeddings.txt")
logger_semantico = setup_logger("logger_semantico", "logs_respuestas_semanticas.txt")

def eliminar_vectores_chroma(path="./chroma"):
    if os.path.exists(path): #  verifica si existe una carpeta (o archivo) en la ruta dada
        shutil.rmtree(path) # elimina recursivamente todo el contenido de esa carpeta.
        logger_embeddings.debug("🗑️ Base vectorial eliminada.")
    else:
        logger_embeddings.debug("⚠️ No existe esa base vectorial.")


