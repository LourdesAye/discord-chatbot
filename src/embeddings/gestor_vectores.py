import os
from langchain_chroma import Chroma
from embeddings.extraer_preguntas import obtener_preguntas_y_metadatos
from utils.utilidades_logs import setup_logger
import psycopg2 
from psycopg2.extras import DictCursor
from utils.conexion_bdd import CONFIG

class GestorBaseVectorial:
    def __init__(self, modelo, persist_directory="./chroma"):
        self.persist_directory = persist_directory
        self.modelo = modelo
        self.logger_embeddings = setup_logger("logger_embeddings", "logs_generacion_embeddings.txt")
        self.vectordb = None

    def existe_base(self):
        if not os.path.exists(self.persist_directory):
            return False
        # Verifica que la carpeta contenga al menos un archivo o subdirectorio real de persistencia
        archivos = os.listdir(self.persist_directory)
        return len(archivos) > 0
    
    def crear_si_no_existe(self, forzar_actualizacion=False):
        if self.existe_base() and not forzar_actualizacion:
            self.logger_embeddings.info("✅ Usando base vectorial existente")
            # no es como Chroma.from_texts, sino que solo carga la base de datos vectorial existente
            self.vectordb = Chroma(persist_directory=self.persist_directory, 
                                embedding_function=self.modelo)
            return self.vectordb
        
        # Verificar si hay datos para crear la base vectorial
        nuevas_preguntas, nuevos_metadatos = obtener_preguntas_y_metadatos()
        if not nuevas_preguntas:
            self.logger_embeddings.error("❌ No hay datos para crear la base vectorial")
            return None

        # Eliminar base existente si se fuerza actualización
        if forzar_actualizacion and self.existe_base():
            self.eliminar_base()
        # Chroma.from_texts necesario si no existe la base de datos vectorial
        # Crea la base de datos vectorial dede cero en el directorio indicado
        # Toma la lista[str] de texts
        # lama al tu modelo_generador_embeddings para pasa los textos para que el modelo calcule los vectores.
        # junta cada Texto + su Vector generado + sus Metadatos para guardarlos en la base de datos vectorial.
        # metadatas en Chroma espera una lista de diccionarios (un diccionario por cada texto)
        # en este caso {"id": fila["id_pregunta"]} por cada pregunta para identificarla.
        self.vectordb = Chroma.from_texts(
            texts=nuevas_preguntas,
            embedding=self.modelo,
            metadatas=nuevos_metadatos,
            persist_directory=self.persist_directory
        )
        self.logger_embeddings.info(f"🔄 Base vectorial {'actualizada' if forzar_actualizacion else 'creada'} con {len(nuevas_preguntas)} preguntas")
        return self.vectordb

    def obtener_respuestas_a_pregunta_con(self, id_pregunta):
        try:
            with psycopg2.connect(**CONFIG) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute("""
                        SELECT r.texto,
                            a.nombre_autor,
                            r.orden,
                            CASE WHEN a.es_docente THEN 'es docente'
                                    ELSE 'no es docente'
                            END AS condicion_docente
                        FROM respuestas r
                        INNER JOIN mensajes m ON r.mensaje_id = m.id_mensaje
                        INNER JOIN autores a ON a.id_autor = m.autor_id
                        WHERE r.pregunta_id = %s
                        ORDER BY r.orden
                    """, (id_pregunta,))
                    resultados = cursor.fetchall()
                    if resultados:
                        self.logger_embeddings.info(f"📊 Total de respuestas obtenidas: {len(resultados)}")
                        return resultados
                    else:
                        self.logger_embeddings.warning(f"⚠️ No se encontró respuesta para id_pregunta: {id_pregunta}")
                        return None
        except psycopg2.Error as e:
            self.logger_embeddings.error(f"💾 Error en consulta SQL: {e}")
            return None
        except Exception as e:
            self.logger_embeddings.error(f"⚠️ Error inesperado: {e}")
            return None


    def buscar(self, pregunta, k=5):
        if not self.vectordb:
            self.logger_embeddings.error("❌ La base vectorial no está cargada.")
            return None
        
        try:
            resultados = self.vectordb.similarity_search_with_score(query=pregunta, k=k)
            
            if not resultados:
                self.logger_embeddings.error(f"❌ No hay resultados de preguntas parecidas a la pregunta: \n ❓'{pregunta}' ❓")
                return None

            resultados_con_similitud = [(doc, 1 - score) for doc, score in resultados]
            resultados_filtrados = [(doc, sim) for doc, sim in resultados_con_similitud if sim > 0]
            resultados_ordenados = sorted(resultados_filtrados, key=lambda x: x[1], reverse=True)
            
            self.logger_embeddings.debug(f"\n❓ PREGUNTA NUEVA: {pregunta}")
            
            for i, (doc, sim) in enumerate(resultados_ordenados, start=1):
                etiqueta = f"🔝 PREGUNTA NÚMERO {i}, LA MÁS PARECIDA:" if i == 1 else f"🔍 PREGUNTA MÁS PARECIDA #{i}:"
                self.logger_embeddings.debug(f"\n{etiqueta}")
                self.logger_embeddings.debug(f"Pregunta: {doc.page_content}")
                self.logger_embeddings.debug(f"Metadatos: {doc.metadata}")
                self.logger_embeddings.debug(f"Similitud: {sim:.4f}")
                
                # Validación segura por si el diccionario no trae la clave id
                pregunta_id = doc.metadata.get("id")
                if not pregunta_id:
                    self.logger_embeddings.warning(f"⚠️ El documento no contiene un 'id' válido en sus metadatos.")
                    continue

                respuestas_recuperadas = self.obtener_respuestas_a_pregunta_con(pregunta_id)
                
                if respuestas_recuperadas:
                    for respuesta in respuestas_recuperadas:
                        self.logger_embeddings.debug(f"\n ✉️ Respuesta Número: {respuesta['orden']}")
                        self.logger_embeddings.debug(f"Texto: {respuesta['texto']}")
                        self.logger_embeddings.debug(f"Nombre del Autor: {respuesta['nombre_autor']}")
                        self.logger_embeddings.debug(f"Condición del Autor: {respuesta['condicion_docente']}")
                else:
                    self.logger_embeddings.debug("⚠️ No hay respuestas registradas para esta pregunta.")
                    
                self.logger_embeddings.debug(f"\n{'-'*80}")

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