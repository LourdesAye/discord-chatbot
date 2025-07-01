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

# por ahora conviven probar_busqueda y responder_a_pregunta
def probar_busqueda(vectordb, pregunta_nueva, k=5):
    # busca en la base vectorial las k preguntas más similares a pregunta_nueva. Estructura: [(documento_1, score_1), (documento_2, score_2), ...]
    resultados = vectordb.similarity_search_with_score(query=pregunta_nueva, k=k)  

    # Convertir distancia a similitud
    resultados_con_similitud = [(doc, 1 - score) for doc, score in resultados]

    # Filtrar resultados con similitud > 0
    resultados_filtrados = [(doc, sim) for doc, sim in resultados_con_similitud if sim > 0]

    # Ordenar de mayor a menor similitud
    resultados_ordenados = sorted(resultados_filtrados, key=lambda x: x[1], reverse=True) # lambda x: x[1] recibe una tupla y agarra el segundo valor de cada elemento como criterio para ordenar. reverse=True significa que el orden debe ser descendente,de mayor a menor.

    logger_embeddings.debug(f" ")
    logger_embeddings.debug(f"❓PREGUNTA NUEVA : {pregunta_nueva}")
    for i, (doc, similitud) in enumerate(resultados_ordenados):
        if i == 0:
            logger_embeddings.debug("🔝 MÁS PARECIDA:")
        else:
            logger_embeddings.debug(f"🔍 Resultado #{i + 1}:")
        logger_embeddings.debug(f"Pregunta: {doc.page_content}")
        logger_embeddings.debug(f"Metadatos: {doc.metadata}")
        logger_embeddings.debug(f"Similitud: {similitud:.4f}")
        logger_embeddings.debug("-" * 40)

# por ahora conviven probar_busqueda y responder_a_pregunta
def responder_a_pregunta(vectordb,pregunta, k=3):
    resultados = vectordb.similarity_search_with_score(query=pregunta, k=k)

    # Convertir a similitud
    resultados_con_similitud = [(doc, 1 - score) for doc, score in resultados]
    resultados_filtrados = [(doc, sim) for doc, sim in resultados_con_similitud if sim > 0]
    resultados_ordenados = sorted(resultados_filtrados, key=lambda x: x[1], reverse=True)

    respuestas = []
    for i, (doc, sim) in enumerate(resultados_ordenados):
        respuesta = doc.page_content  # ya que es un documento con texto directamente
        respuestas.append(f"Respuesta {i + 1}: {respuesta}")

        # Log
        logger_semantico.debug(f"🧠 Pregunta: {pregunta}")
        logger_semantico.debug(f"🔍 Resultado #{i + 1}: {respuesta}")
        logger_semantico.debug(f"Similitud: {sim:.4f}")
        logger_semantico.debug("-" * 40)

    return "\n\n".join(respuestas) if respuestas else "❌ No encontré respuestas relevantes."


