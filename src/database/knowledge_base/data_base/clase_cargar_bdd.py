from psycopg2 import connect
from database.knowledge_base.models.clase_preguntas import Pregunta
from database.knowledge_base.models.clase_respuestas import Respuesta
from dateutil.parser import isoparse
from psycopg2.extras import RealDictCursor
from database.knowledge_base.utils.utilidades_logs import setup_logger
import traceback
from database.knowledge_base.models.clase_autores import docentes 
from database.knowledge_base.utils.utilidades_logs import guardar_pregunta_y_respuestas_en_log

# agregando logger para seguimiento de la carga de datos
logger_db= setup_logger('carga_db','log_persistencia_de_datos.txt')

class GestorBD:
    def __init__(self, config):
        self.conn = connect(
            dbname=config["dbname"],
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
        )
        self.docentes = docentes

    def es_docente(self, nombre_usuario):
        return nombre_usuario in self.docentes

    def insertar_o_obtener_autor(self, nombre_autor):
        logger_db.debug(f"Se inserta o se obtiene autor")
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id_autor FROM autores WHERE nombre_autor = %s", (nombre_autor,))
            fila = cur.fetchone()
            if fila:
                logger_db.debug(f"El autor {nombre_autor} existe en la base de datos")
                return fila["id_autor"]
            logger_db.debug(f"El autor {nombre_autor} NO existe en la base de datos, se lo va a ingresar")
            cur.execute(
                """
                INSERT INTO autores (nombre_autor, es_docente)
                VALUES (%s, %s) RETURNING id_autor
                """,
                (nombre_autor, self.es_docente(nombre_autor))
            )
            return cur.fetchone()["id_autor"]

    def insertar_mensaje(self, id_mensaje_discord, autor_id, fecha_mensaje,
                         contenido, es_pregunta=False, origen=None):
        logger_db.debug(f"Se va a ingresar un nuevo mensaje a la base de datos : {contenido}")
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO mensajes (
                    id_mensaje_discord,
                    autor_id,
                    fecha_mensaje,
                    contenido,
                    es_pregunta,
                    origen
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_mensaje
                """,
                (
                    id_mensaje_discord,
                    autor_id,
                    fecha_mensaje,
                    contenido,
                    es_pregunta,
                    origen
                )
            )
            return cur.fetchone()["id_mensaje"]

    def insertar_attachment(self, mensaje_id, nombre_archivo, tipo_archivo):
        logger_db.debug(f"se inserta un nuevo archivo adjunto llamado { nombre_archivo} asociado al mensaje {mensaje_id}")
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO adjuntos (mensaje_id, url, tipo)
                VALUES (%s, %s, %s)
                RETURNING id_adjunto
                """,
                (mensaje_id, nombre_archivo, tipo_archivo)
            )
            return cur.fetchone()["id_adjunto"]

    def insertar_pregunta(self, pregunta: Pregunta, id_mensaje):
        logger_db.debug(f"se agrega una nueva pregunta a la base de datos : {pregunta.contenido} asociado al mensaje {id_mensaje}")
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO preguntas (mensaje_id, texto, esta_cerrada, sin_contexto, es_administrativa)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_pregunta
                """,
                (id_mensaje, pregunta.contenido, pregunta.cerrada,pregunta.sin_contexto,pregunta.es_administrativa)
            )
            return cur.fetchone()["id_pregunta"]

    def insertar_respuesta(self, respuesta: Respuesta, mensaje_id, pregunta_id, orden):
        logger_db.debug(f"se agrega una nueva respuesta : {respuesta.contenido} asociado al mensaje {mensaje_id} y a la pregunta {pregunta_id}")
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO respuestas (mensaje_id, pregunta_id, texto, orden, es_validada, es_corta)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_respuesta
                """,
                (mensaje_id, pregunta_id, respuesta.contenido, orden, respuesta.es_validada, respuesta.es_corta)
            )
            return cur.fetchone()["id_respuesta"]

    def convertir_a_datetime(self, timestamp_str):
        logger_db.debug(f"se covierte: {timestamp_str} a un datetime")
        return isoparse(timestamp_str)

    def persistir_preguntas(self, preguntas_cerradas: list[Pregunta],index):
        logger_db.debug(" ... ingresando a la persistencia de datos ... ")
        logger_db.debug (f"... se va a procesar en JSON {index} ... ")
        cont_preg_sin_resp=0
        nombre_ruta = (f"log_preg_sin_respuestas_{index}")
        preguntas_a_persistir =[]

        for indice,pregunta in enumerate(preguntas_cerradas, start=1):
            if len(pregunta.respuestas) == 0:
                cont_preg_sin_resp= cont_preg_sin_resp +1
                self.guardar_pregunta_sin_respuesta_en_log(pregunta,indice,nombre_ruta,cont_preg_sin_resp,)
            else:
                preguntas_a_persistir.append(pregunta)

        ruta_preg_persistidas = (f"log_preguntas_efectivamente_pesistidas_{index}")
        logger_db.debug(f" ... SE VAN A PERSISTIR {len(preguntas_a_persistir)} PREGUNTAS CERRADAS EN LA BASE DE DATOS ...")
        try:
            for idx, pregunta in enumerate(preguntas_a_persistir, start=1):
                guardar_pregunta_y_respuestas_en_log(pregunta,idx,ruta_preg_persistidas)
            
                logger_db.debug(f"\n📌 [{idx}/{len(preguntas_a_persistir)}] Procesando un mensaje que es pregunta: {pregunta.contenido} del autor {pregunta.autor}")
                autor_id = self.insertar_o_obtener_autor(pregunta.autor)
                logger_db.debug(f" se obtuvo un autor_id: {autor_id} para la pregunta")
               
                mensaje_id = self.insertar_mensaje(
                    id_mensaje_discord=pregunta.id_pregunta,
                    autor_id=autor_id,
                    fecha_mensaje=pregunta.timestamp,
                    contenido=pregunta.contenido,
                    es_pregunta=True,
                    origen=pregunta.origen
                )
                logger_db.debug(f" se obtuvo un mensaje_id: {mensaje_id} para la pregunta")
                logger_db.debug(f" Se van a guardar los archivos adjuntos asociados")
                
                for nombre_archivo, tipo in pregunta.attachments: 
                    self.insertar_attachment(mensaje_id, nombre_archivo, tipo)

                id_pregunta = self.insertar_pregunta(pregunta, mensaje_id)

                # se ordenan las preguntas por fecha de la más antigua a la más actual
                logger_db.debug(f" se ordenan las respuestas de la pregunta {idx} cuyo id es {id_pregunta}")
                respuestas_ordenadas = sorted(pregunta.respuestas, key=lambda r: self.convertir_a_datetime(r.timestamp))
                for orden, respuesta in enumerate(respuestas_ordenadas,start=1): # por defecto empieza en 0 
                    logger_db.debug(f" se almacena la respuesta {orden} para la pregunta")
                    autor_id_r = self.insertar_o_obtener_autor(respuesta.autor)
                    mensaje_id_r = self.insertar_mensaje(
                        id_mensaje_discord=respuesta.id_respuesta,
                        autor_id=autor_id_r,
                        fecha_mensaje=respuesta.timestamp,
                        contenido=respuesta.contenido,
                        es_pregunta=False,
                        origen=respuesta.origen
                    )
                    logger_db.debug(f" se obtuvo un mensaje_id: {mensaje_id_r} para la respuesta")
                    logger_db.debug(f" Se van a guardar los archivos adjuntos asociados")
                    for nombre_archivo, tipo in respuesta.attachments:
                        self.insertar_attachment(mensaje_id_r, nombre_archivo, tipo)

                    self.insertar_respuesta(respuesta, mensaje_id_r, id_pregunta, orden)
            self.conn.commit()
        except Exception as e:
            logger_db.debug(f"❌ Error al persistir las preguntas y respuestas: {e}")
            logger_db.debug(traceback.format_exc())
            if self.conn:
                self.conn.rollback()
                logger_db.debug("⛔ Transacción revertida debido al error.")

    def cerrar_conexion(self):
        self.conn.commit()
        self.conn.close()
