import os
from langchain_chroma import Chroma
from embeddings.extraer_preguntas import obtener_preguntas_y_metadatos
from utils.utilidades_logs import setup_logger

class GestorBaseVectorial:
    def __init__(self, modelo, persist_directory="./chroma"):
        self.persist_directory = persist_directory
        self.modelo = modelo
        self.logger_embeddings = setup_logger("logger_embeddings", "logs_generacion_embeddings.txt")
        self.vectordb = None

    def existe_base(self):
        return os.path.exists(self.persist_directory) and os.listdir(self.persist_directory)
    
    def crear_si_no_existe(self, forzar_actualizacion=False):
        if self.existe_base() and not forzar_actualizacion:
            self.logger_embeddings.info("✅ Usando base vectorial existente")
            self.vectordb = Chroma(persist_directory=self.persist_directory, 
                                embedding_function=self.modelo)
            return self.vectordb
        
        # Verificar si hay datos nuevos
        nuevas_preguntas, nuevos_metadatos = obtener_preguntas_y_metadatos()
        if not nuevas_preguntas:
            self.logger_embeddings.error("❌ No hay datos para crear la base vectorial")
            return None

        # Eliminar base existente si se fuerza actualización
        if forzar_actualizacion and self.existe_base():
            self.eliminar_base()

        self.vectordb = Chroma.from_texts(
            texts=nuevas_preguntas,
            embedding=self.modelo,
            metadatas=nuevos_metadatos,
            persist_directory=self.persist_directory
        )
        self.logger_embeddings.info(f"🔄 Base vectorial {'actualizada' if forzar_actualizacion else 'creada'} con {len(nuevas_preguntas)} preguntas")
        return self.vectordb

    def buscar(self, pregunta, k=5):
        if not self.vectordb:
            self.logger_embeddings.error("❌ La base vectorial no está cargada.")
            return None
        
        try:
            resultados = self.vectordb.similarity_search_with_score(query=pregunta, k=k)
            resultados_con_similitud = [(doc, 1 - score) for doc, score in resultados]
            resultados_filtrados = [(doc, sim) for doc, sim in resultados_con_similitud if sim > 0]
            resultados_ordenados = sorted(resultados_filtrados, key=lambda x: x[1], reverse=True)
            # def obtener_segundo(x):return x[1] y ordenados = sorted(lista, key=obtener_segundo)
            # lambda reemplaza la definición con def
            # sorted (secuencia_a_ordenar,criterio_de_orden,reverse= orden_ascendente_true_o_decendente_false)
            
            self.logger_embeddings.debug(f"\n❓PREGUNTA NUEVA: {pregunta}")
            for i, (doc, sim) in enumerate(resultados_ordenados):
                etiqueta = "🔝 MÁS PARECIDA:" if i == 0 else f"🔍 Resultado #{i + 1}:"
                self.logger_embeddings.debug(etiqueta)
                self.logger_embeddings.debug(f"Pregunta: {doc.page_content}")
                self.logger_embeddings.debug(f"Metadatos: {doc.metadata}")
                self.logger_embeddings.debug(f"Similitud: {sim:.4f}")
                self.logger_embeddings.debug("-" * 40)
            
            if not resultados_ordenados:
                self.logger_embeddings.error(f"❌ No hay resultados de preguntas parecidas a la pregunta: \n  ❓'{pregunta}' ❓")
                return None
            else:
                return resultados_ordenados
        
        except Exception as e:
            self.logger_embeddings.error(f"❌ Error en la búsqueda: {str(e)}")
            return None
        
    def eliminar_base(self):
        import shutil
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            self.logger_embeddings.debug("🗑️ Base vectorial eliminada.")
        else:
            self.logger_embeddings.debug("⚠️ No existe la base vectorial a eliminar.")
    
    def verificar_consistencia(self):
        """Compara conteo de preguntas en BDD vs VectorDB"""
        preguntas_bdd, _ = obtener_preguntas_y_metadatos()
        if not self.vectordb:
            self.logger_embeddings.warning("⚠️ No se puede verificar consistencia: VectorDB no cargada")
            return False
        conteo_vectordb = self.vectordb._collection.count()
        dif = abs(len(preguntas_bdd) - conteo_vectordb)
        
        if dif > 0:
            self.logger_embeddings.warning(
                f"🔍 Inconsistencia detectada: BDD={len(preguntas_bdd)} vs VectorDB={conteo_vectordb}"
            )
            return False
        return True