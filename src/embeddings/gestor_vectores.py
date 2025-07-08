import os
from langchain_community.vectorstores import Chroma
from embeddings.extraer_preguntas import obtener_preguntas_y_metadatos
from utils_for_all.utilidades_logs import setup_logger

class GestorBaseVectorial:
    def __init__(self, modelo, persist_directory="./chroma"):
        self.persist_directory = persist_directory
        self.modelo = modelo
        self.logger_embeddings = setup_logger("logger_embeddings", "logs_generacion_embeddings.txt")
        self.logger_semantico = setup_logger("logger_semantico", "logs_respuestas_semanticas.txt")
        self.vectordb = None

    def existe_base(self):
        return os.path.exists(self.persist_directory) and os.listdir(self.persist_directory)

    def crear_si_no_existe(self):
        if self.existe_base():
            self.logger_embeddings.debug("✅ Base vectorial ya existe. No se creó nuevamente.")
            self.vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=self.modelo)
            return self.vectordb

        preguntas, metadatos = obtener_preguntas_y_metadatos()
        if not preguntas:
            self.logger_embeddings.debug("⚠️ No se generaron embeddings por falta de preguntas.")
            return None

        self.vectordb = Chroma.from_texts(
            texts=preguntas,
            embedding=self.modelo,
            metadatas=metadatos,
            persist_directory=self.persist_directory
        )
        self.logger_embeddings.debug("✅ Base vectorial creada con éxito.")
        return self.vectordb

    def buscar(self, pregunta, k=5):
        if not self.vectordb:
            self.logger_embeddings.error("❌ La base vectorial no está cargada.")
            return

        resultados = self.vectordb.similarity_search_with_score(query=pregunta, k=k)
        resultados_con_similitud = [(doc, 1 - score) for doc, score in resultados]
        resultados_filtrados = [(doc, sim) for doc, sim in resultados_con_similitud if sim > 0]
        resultados_ordenados = sorted(resultados_filtrados, key=lambda x: x[1], reverse=True)

        self.logger_embeddings.debug(f"\n❓PREGUNTA NUEVA: {pregunta}")
        for i, (doc, sim) in enumerate(resultados_ordenados):
            etiqueta = "🔝 MÁS PARECIDA:" if i == 0 else f"🔍 Resultado #{i + 1}:"
            self.logger_embeddings.debug(etiqueta)
            self.logger_embeddings.debug(f"Pregunta: {doc.page_content}")
            self.logger_embeddings.debug(f"Metadatos: {doc.metadata}")
            self.logger_embeddings.debug(f"Similitud: {sim:.4f}")
            self.logger_embeddings.debug("-" * 40)

    def responder(self, pregunta, k=3):
        if not self.vectordb:
            self.logger_semantico.error("❌ La base vectorial no está cargada.")
            return "❌ No hay base vectorial disponible."

        resultados = self.vectordb.similarity_search_with_score(query=pregunta, k=k)
        resultados_con_similitud = [(doc, 1 - score) for doc, score in resultados]
        resultados_filtrados = [(doc, sim) for doc, sim in resultados_con_similitud if sim > 0]
        resultados_ordenados = sorted(resultados_filtrados, key=lambda x: x[1], reverse=True)

        respuestas = []
        for i, (doc, sim) in enumerate(resultados_ordenados):
            respuesta = doc.page_content
            respuestas.append(f"Respuesta {i + 1}: {respuesta}")

            self.logger_semantico.debug(f"🧠 Pregunta: {pregunta}")
            self.logger_semantico.debug(f"🔍 Resultado #{i + 1}: {respuesta}")
            self.logger_semantico.debug(f"Similitud: {sim:.4f}")
            self.logger_semantico.debug("-" * 40)

        return "\n\n".join(respuestas) if respuestas else "❌ No encontré respuestas relevantes."
    
    def eliminar_base(self):
        import shutil
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            self.logger_embeddings.debug("🗑️ Base vectorial eliminada.")
        else:
            self.logger_embeddings.debug("⚠️ No existe la base vectorial a eliminar.")