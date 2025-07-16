from psycopg2 import connect, sql, errors
from database.knowledge_base.models.clase_preguntas import Pregunta
from database.knowledge_base.models.clase_respuestas import Respuesta
from dateutil.parser import isoparse
from psycopg2.extras import RealDictCursor
from utils_for_all.utilidades_logs import setup_logger
import traceback
from database.knowledge_base.models.clase_autores import lista_docentes 
from utils_for_all.utilidades_logs import guardar_pregunta_y_respuestas_en_log
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# agregando logger para seguimiento de la carga de datos
logger_db= setup_logger('carga_db','log_persistencia_de_datos.txt')

class GestorBD:
    def __init__(self, config):
        self.config = config
        self.docentes = lista_docentes
        self._initialize_database() # verifica si existe la bdd, en caso de que no la crea
        self.conn = self._connect_to_database() # una vez creada o validando existencia se conecta a ella
        self._initialize_tables() # agrega a los autores docentes

    def _initialize_database(self):
        """Crea la base de datos si no existe"""
        # Conexión temporal sin especificar la base de datos
        temp_conn = connect(
            user=self.config["user"],
            password=self.config["password"],
            host=self.config["host"],
            port=self.config["port"]
        )
        # para CREATE DATABASE o configuraciones que no pueden ejecutarse dentro de una transacción (cada instrucción se ejecuta de inmediato).
        temp_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        try:
            with temp_conn.cursor() as cur:
                # Verificar si la base de datos existe : devuelve una columna si existe la base de datos
                cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), 
                            [self.config["dbname"]])
                exists = cur.fetchone()
                
                if not exists:
                    logger_db.info(f"Creando base de datos {self.config['dbname']}...")
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(self.config["dbname"]))
                    )
                    logger_db.info("Base de datos creada exitosamente")
        except errors.DatabaseError as e:
            logger_db.error(f"Error al crear la base de datos: {e}")
        finally:
            temp_conn.close()

    def _connect_to_database(self):
        """Establece conexión con la base de datos"""
        try:
            conn = connect(
                dbname=self.config["dbname"],
                user=self.config["user"],
                password=self.config["password"],
                host=self.config["host"],
                port=self.config["port"],
            )
            logger_db.info("Conexión a la base de datos establecida")
            return conn
        except errors.OperationalError as e:
            logger_db.error(f"Error al conectar a la base de datos: {e}")
            raise

    def _initialize_tables(self):
        """Crea las tablas si no existen"""
        tables = {
            "autores": """
                CREATE TABLE IF NOT EXISTS autores (
                    id_autor SERIAL PRIMARY KEY,
                    nombre_autor TEXT NOT NULL,
                    es_docente BOOLEAN NOT NULL
                )
            """,
            "mensajes": """
                CREATE TABLE IF NOT EXISTS mensajes (
                    id_mensaje SERIAL PRIMARY KEY,
                    id_mensaje_discord BIGINT NOT NULL,
                    autor_id INTEGER NOT NULL REFERENCES autores(id_autor) ON DELETE CASCADE,
                    fecha_mensaje TIMESTAMP NOT NULL,
                    contenido TEXT NOT NULL,
                    es_pregunta BOOLEAN DEFAULT FALSE,
                    origen TEXT
                )
            """,
            "adjuntos": """
                CREATE TABLE IF NOT EXISTS adjuntos (
                    id_adjunto SERIAL PRIMARY KEY,
                    mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
                    url TEXT NOT NULL,
                    tipo TEXT
                )
            """,
            "preguntas": """
                CREATE TABLE IF NOT EXISTS preguntas (
                    id_pregunta SERIAL PRIMARY KEY,
                    mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
                    texto TEXT NOT NULL,
                    esta_cerrada BOOLEAN DEFAULT FALSE,
                    sin_contexto BOOLEAN DEFAULT FALSE,
                    es_administrativa BOOLEAN DEFAULT FALSE

                )
            """,
            "respuestas": """
                CREATE TABLE IF NOT EXISTS respuestas (
                    id_respuesta SERIAL PRIMARY KEY,
                    mensaje_id INTEGER REFERENCES mensajes(id_mensaje),
                    pregunta_id INTEGER REFERENCES preguntas(id_pregunta),
                    texto TEXT NOT NULL,
                    orden INTEGER NOT NULL,
                    es_validada BOOLEAN DEFAULT FALSE,
                    es_corta BOOLEAN DEFAULT FALSE
                )
            """
        }
        
        try:
            with self.conn.cursor() as cur:
                for table_name, table_ddl in tables.items():
                    cur.execute(table_ddl)
                self.conn.commit()
                logger_db.info("Tablas creadas/verificadas exitosamente")
                
                # Opcional: Insertar datos iniciales si es necesario
                self._insert_initial_data()
                
        except errors.DatabaseError as e:
            logger_db.error(f"Error al crear tablas: {e}")
            self.conn.rollback()
            raise
    
    def _insert_initial_data(self):
        """Inserta datos iniciales si las tablas están vacías"""
        try:
            with self.conn.cursor() as cur:
                # Verificar si la tabla autores está vacía
                cur.execute("SELECT COUNT(*) FROM autores")
                count = cur.fetchone()[0]
                
                if count == 0 and self.docentes:
                    logger_db.info("Insertando datos iniciales de autores...")
                    for docente in self.docentes:
                        cur.execute(
                            "INSERT INTO autores (nombre_autor, es_docente) VALUES (%s, %s)",
                            (docente, True)
                        )
                    self.conn.commit()
                    logger_db.info("Datos iniciales de autores insertados")
        except errors.DatabaseError as e:
            logger_db.error(f"Error al insertar datos iniciales: {e}")
            self.conn.rollback()


    def es_docente(self, nombre_usuario):
        return nombre_usuario in self.docentes

    def insertar_o_obtener_autor(self, nombre_autor):
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
        tipo_mensaje = "PREGUNTA" if es_pregunta else "RESPUESTA"
        logger_db.debug(f"Se va a ingresar un mensaje ({tipo_mensaje}) a la base de datos : {contenido}")
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
        return isoparse(timestamp_str)

    def persistir_preguntas(self, preguntas_cerradas: list[Pregunta],index):
        logger_db.debug(" 🗄️ Persistencia de datos")
        logger_db.debug (f" 📁 se va a procesar en JSON {index} ... ")
        cont_preg_sin_resp=0
        nombre_ruta = (f"log_preg_sin_respuestas_{index}")
        preguntas_a_persistir =[]

        for indice,pregunta in enumerate(preguntas_cerradas, start=1):
            if len(pregunta.respuestas) == 0:
                cont_preg_sin_resp= cont_preg_sin_resp +1
                self.guardar_pregunta_sin_respuesta_en_log(pregunta,indice,nombre_ruta,cont_preg_sin_resp,)
            else:
                preguntas_a_persistir.append(pregunta)

        ruta_preg_persistidas = (f"log_preguntas_efectivamente_pesistidas_{index}.txt")
        logger_db.debug(f" 🗄️ Se van a persistir {len(preguntas_a_persistir)} preguntas cerradas")
        try:
            for idx, pregunta in enumerate(preguntas_a_persistir, start=1):
                guardar_pregunta_y_respuestas_en_log(pregunta,idx,ruta_preg_persistidas)
            
                logger_db.debug(f"\n📌 [{idx}/{len(preguntas_a_persistir)}] Procesando un mensaje que es pregunta: \n{pregunta.contenido} \n Autor: {pregunta.autor}")
                autor_id = self.insertar_o_obtener_autor(pregunta.autor)
                logger_db.debug(f"👤 Se obtuvo un el id para el autor: {autor_id} ")
               
                mensaje_id = self.insertar_mensaje(
                    id_mensaje_discord=pregunta.id_pregunta,
                    autor_id=autor_id,
                    fecha_mensaje=pregunta.timestamp,
                    contenido=pregunta.contenido,
                    es_pregunta=True,
                    origen=pregunta.origen
                )
                logger_db.debug(f" ✉️ se obtuvo un mensaje_id (para la pregunta): {mensaje_id}")
                
                for nombre_archivo, tipo in pregunta.attachments: 
                    self.insertar_attachment(mensaje_id, nombre_archivo, tipo)
                
                logger_db.debug(f" 📁 Se insertaron en la base de datos los nombres archivos adjuntos asociados")

                id_pregunta = self.insertar_pregunta(pregunta, mensaje_id)
                logger_db.debug(f" 💾 Se persiste pregunta en la base de datos")

                # se ordenan las preguntas por fecha de la más antigua a la más actual
                logger_db.debug(f" 📩 Se ordenan sus respuestas para ser persistidas")
                respuestas_ordenadas = sorted(pregunta.respuestas, key=lambda r: self.convertir_a_datetime(r.timestamp))
                for orden, respuesta in enumerate(respuestas_ordenadas,start=1): # por defecto empieza en 0
                    logger_db.debug(f"")
                    logger_db.debug(f" 📩 respuesta {orden} : {respuesta.contenido}")
                    autor_id_r = self.insertar_o_obtener_autor(respuesta.autor)
                    mensaje_id_r = self.insertar_mensaje(
                        id_mensaje_discord=respuesta.id_respuesta,
                        autor_id=autor_id_r,
                        fecha_mensaje=respuesta.timestamp,
                        contenido=respuesta.contenido,
                        es_pregunta=False,
                        origen=respuesta.origen
                    )
                    logger_db.debug(f" ✉️ se obtuvo un mensaje_id (para la respuesta): {mensaje_id_r}")
                    for nombre_archivo, tipo in respuesta.attachments:
                        self.insertar_attachment(mensaje_id_r, nombre_archivo, tipo)
                    logger_db.debug(f" 📁 Se insertaron en la base de datos los nombres archivos adjuntos asociados")
                    self.insertar_respuesta(respuesta, mensaje_id_r, id_pregunta, orden)
                    logger_db.debug(f" 💾 Se persiste al repuesta en la base de datos")
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