import os
from psycopg2 import connect
from clase_preguntas import Pregunta
from clase_respuestas import Respuesta
from dateutil.parser import isoparse
import sys
from psycopg2.extras import RealDictCursor

class GestorBD:
    def __init__(self, config):
        self.conn = connect(
            dbname=config["dbname"],
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
        )
        print(f"✅ Te conectaste a la base de datos")
        self.docentes = config["docentes"]

    def es_docente(self, nombre_usuario):
        return nombre_usuario in self.docentes

    def insertar_o_obtener_autor(self, nombre_autor):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id_autor FROM autores WHERE nombre_autor = %s", (nombre_autor,))
            fila = cur.fetchone()
            if fila:
                return fila["id_autor"]
            cur.execute(
                """
                INSERT INTO autores (nombre_autor, es_docente)
                VALUES (%s, %s) RETURNING id_autor
                """,
                (nombre_autor, self.es_docente(nombre_autor))
            )
            return cur.fetchone()["id_autor"]

    def insertar_mensaje(self, id_mensaje_discord, autor_id, fecha_mensaje,
                         contenido, es_pregunta=False, es_respuesta=False, origen=None):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO mensajes (
                    id_mensaje_discord,
                    autor_id,
                    fecha_mensaje,
                    contenido,
                    es_pregunta,
                    es_respuesta,
                    origen
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_mensaje
                """,
                (
                    id_mensaje_discord,
                    autor_id,
                    fecha_mensaje,
                    contenido,
                    es_pregunta,
                    es_respuesta,
                    origen
                )
            )
            return cur.fetchone()["id_mensaje"]

    def insertar_attachment(self, mensaje_id, nombre_archivo, tipo_archivo):
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
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO preguntas (mensaje_id, texto, esta_cerrada)
                VALUES (%s, %s, %s)
                RETURNING id_pregunta
                """,
                (id_mensaje, pregunta.contenido, True)
            )
            return cur.fetchone()["id_pregunta"]

    def insertar_respuesta(self, respuesta: Respuesta, mensaje_id, pregunta_id, orden):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO respuestas (mensaje_id, pregunta_id, texto, orden, es_validada)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_respuesta
                """,
                (mensaje_id, pregunta_id, respuesta.contenido, orden, respuesta.es_validada)
            )
            return cur.fetchone()["id_respuesta"]

    def convertir_a_datetime(self, timestamp_str):
        return isoparse(timestamp_str)

    def persistir_preguntas(self, preguntas_cerradas: list[Pregunta]):
        print(" ... ingresando a la persistencia de datos ... ")
        print(f"🧠 Persistiendo {len(preguntas_cerradas)} preguntas cerradas en la base de datos...")
        try:
            for idx, pregunta in enumerate(preguntas_cerradas, start=1):
                print(f"\n📌 [{idx}/{len(preguntas_cerradas)}] Procesando un mensaje que es pregunta: {pregunta.contenido} del autor {pregunta.autor}")
                autor_id = self.insertar_o_obtener_autor(pregunta.autor)
                mensaje_id = self.insertar_mensaje(
                    id_mensaje_discord=pregunta.id_pregunta,
                    autor_id=autor_id,
                    fecha_mensaje=pregunta.timestamp,
                    contenido=pregunta.contenido,
                    es_pregunta=True,
                    origen=pregunta.origen
                )

                for nombre_archivo, tipo in pregunta.attachments:
                    self.insertar_attachment(mensaje_id, nombre_archivo, tipo)

                id_pregunta = self.insertar_pregunta(pregunta, mensaje_id)

                respuestas_ordenadas = sorted(pregunta.respuestas, key=lambda r: self.convertir_a_datetime(r.timestamp))
                for orden, respuesta in enumerate(respuestas_ordenadas):
                    autor_id_r = self.insertar_o_obtener_autor(respuesta.autor)
                    mensaje_id_r = self.insertar_mensaje(
                        id_mensaje_discord=respuesta.id_respuesta,
                        autor_id=autor_id_r,
                        fecha_mensaje=respuesta.timestamp,
                        contenido=respuesta.contenido,
                        es_respuesta=True,
                        origen=respuesta.origen
                    )
                    for nombre_archivo, tipo in respuesta.attachments:
                        self.insertar_attachment(mensaje_id_r, nombre_archivo, tipo)

                    self.insertar_respuesta(respuesta, mensaje_id_r, id_pregunta, orden)
            self.conn.commit()
        except Exception as e:
            print(f"❌ Error al persistir las preguntas y respuestas: {e}")
            if self.conn:
                self.conn.rollback()
                print("⛔ Transacción revertida debido al error.")

    def cerrar_conexion(self):
        self.conn.commit()
        self.conn.close()
        print("🧾 Conexión a la base de datos cerrada y cambios guardados.")