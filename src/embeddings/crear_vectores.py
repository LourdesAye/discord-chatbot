import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"  # Para desactivar telemetría en ChromaDB
os.environ["LANGCHAIN_TRACING"] = "False"  # Para desactivar telemetría en LangChain
os.environ["OTEL_SDK_DISABLED"] = "true"  # Para desactivar telemetría en OpenTelemetry
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from embeddings.extraer_preguntas import obtener_preguntas_y_metadatos
from utils_for_all.utilidades_logs import setup_logger

# se activa telemetría automáticamente en LangChain/CromaDB porque utilizan opentelemetry y posthog internamente 
# para recolectar métricas de uso.
# VS Code también intenta enviar telemetría, generando un conflicto con los argumentos de las funciones. 
# Desactivar telemetría en Chroma/LangChain

def crear_base_vectorial():
    logger_embeddings = setup_logger("logger_embeddings", "logs_generacion_embeddings.txt")
    preguntas, metadatos = obtener_preguntas_y_metadatos()
    if not preguntas:
        logger_embeddings.debug("⚠️ No se generaron embeddings por falta de preguntas.")
        return None
    modelo = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_texts(
        texts=preguntas,
        embedding=modelo,
        metadatas=metadatos,
        persist_directory="./chroma",
        anonymized_telemetry=False  # 👈 Desactiva telemetría aquí
    )
    logger_embeddings.debug("✅ Base vectorial creada con éxito.")
    return vectordb

def get_base_de_datos_vectorial(): 
    # Carga de modelo y base vectorial persistente
    modelo = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(persist_directory="./chroma", embedding_function=modelo)