from processing.procesamiento_completo import ProcesadorBase
from processing.estrategias_cierre_mensajes.estrategias_cierre_mensajes import EstrategiaCierreTiempoReal
from psycopg2 import connect, sql, errors
from utils.conexion_bdd import CONFIG
from utils.utilidades_logs import setup_logger
from psycopg2.extras import RealDictCursor
# Estor sería del preguntasRepository
from database.models.clase_mensajes import Mensaje
from database.models.clase_preguntas import Pregunta
from database.models.clase_respuestas import Respuesta
from database.models.clase_autores import Autores
from datetime import datetime

logger_db_cargada = setup_logger('cargando_datos_desde_bdd', 'log_cargando_datos_desde_base_de_datos_existente.txt')

# sería el Repository

class ProcesadorTiempoReal(ProcesadorBase):
    # definición explícita solo por claridad del constructor aunque no hace falta
    def __init__(self, nombre_log, estrategias=None):
        # mismos atributos que clase base
        super().__init__(nombre_log, estrategias)
        self.estrategia_cierre = EstrategiaCierreTiempoReal()  # estrategia de cierre para tiempo real
        # se agregan atributos para conexión a base de datos
        self.config = CONFIG
        self.conn = self.connect_to_database()

    def connect_to_database(self):
        """Establece conexión con la base de datos"""
        try:
            # a partir del diccionario config, se pasan los parámetros necesarios para la conexión
            conn = connect(
                dbname=self.config["dbname"],
                user=self.config["user"],
                password=self.config["password"],
                host=self.config["host"],
                port=self.config["port"],
            )
            # logger de que la conexión fue exitosa
            logger_db_cargada.info("Conexión a la base de datos establecida")
            return conn
        except errors.OperationalError as e:
            logger_db_cargada.error(f"Error al conectar a la base de datos: {e}")
            raise
    

    @property # para que se interprete como atributo (self.preguntas_abiertas) y no como método (self.preguntas_abiertas())
    def preguntas_abiertas(self):
        """Consulta dinámica a la base de datos para obtener preguntas abiertas."""
        # query o consulta a la base de datos para traer preguntas abiertas uniendo tablas preguntas, mensajes y autores
        query = """
        SELECT 
            p.id_pregunta, p.texto AS texto_pregunta, p.esta_cerrada, 
            p.sin_contexto, p.es_administrativa,
            m.id_mensaje AS id_mensaje_bd, m.id_mensaje_discord,
            m.fecha_mensaje, m.origen,
            a.id_autor, a.nombre_autor, a.es_docente
        FROM preguntas p
        JOIN mensajes m ON p.mensaje_id = m.id_mensaje
        JOIN autores a ON m.autor_id = a.id_autor
        WHERE p.esta_cerrada = FALSE
        ORDER BY p.id_pregunta;
        """
        # ANALIZAR SI SE NECESITA REALMENTE: 
            # p.sin_contexto, p.es_administrativa
            # m.id_mensaje_discord, m.origen
            # a.is_autor, a.nombre_autor, a.es_docente
        # NO NECESITO m.es_pregunta porque ya se sabe que son preguntas abiertas el join se hace con la tabla preguntas

        # conn (connection) → es la conexión a la base de datos PostgreSQL (puente entre código de Python y la base de datos).
        # cursor → es un objeto que permite ejecutar consultas SQL y recuperar resultados.
        # RealDictCursor → tipo especial de cursor que devuelve cada fila de una consulta PostgreSQL como diccionarios {nombre_columnas: datos} 
        # en lugar de tupla (datos sueltos sin nombre_columna). Esto hace que cada fila devuelta sea un diccionario, no una tupla.
        # execute() → método para enviar la consulta SQL a la base de datos
        # fetchall() → devuelve una lista de filas donde fila es un diccionario (porque se usa RealDictCursor)
            # ejemplo: [
                # {
                    # 'id_pregunta': 1, 
                    # 'mensaje_id': 1, 
                    # 'texto': 'buenas, que tal? no pude acceder al repo del equipo, intente entrando desde https://github.com/dds-utn/2024-tpa-mi-no-grupo-15 la clase que se unieron al repo no pude asistir, y cuando intente despues no pude', 
                    # 'esta_cerrada': True,
                    # 'sin_contexto': False,
                    # 'es_administrativa': False,},
                    # {...},
                    # {...}]

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:  # se establece conexión con la base de datos y se crea un cursor para ejecutar la consulta
            cur.execute(query) # enviar la consulta SQL a la base de datos
            rows = cur.fetchall() # obtener todas las filas resultantes de la consulta

        preguntas = []
        for row in rows: # iterar sobre cada fila (diccionario) devuelta por la consulta

            autor = Autores(  # construir el autor PERO ANALIZAR SI REALMENTE ES NECESARIO
                id_autor=row["id_autor"],
                nombre_autor=row["nombre_autor"],
                es_docente=row["es_docente"]
            )

            mensaje = Mensaje(  # construir el mensaje
                id_mensaje=row["id_mensaje_discord"], # ANALIZAR SI REALMENTE ES NECESARIO
                autor=autor.nombre_autor, # ANALIZAR SI REALMENTE ES NECESARIO
                contenido=row["texto_pregunta"],
                timestamp=row["fecha_mensaje"].isoformat(), # ANALIZAR SI REALMENTE ES NECESARIO es isofomat() o hay que hacer alguna conversión
                attachments=[],  # ANALIZAR SI REALMENTE ES NECESARIO
                origen=row["origen"] # ANALIZAR SI REALMENTE ES NECESARIO
            )
            mensaje.id_mensaje_base_de_datos = row["id_mensaje_bd"]

            mensaje.attachements = []  # aquí cargar attachments

            pregunta = Pregunta(mensaje) # construir la pregunta
            pregunta.id_pregunta = row["id_pregunta"]
            pregunta.cerrada = row["esta_cerrada"]
            pregunta.attachments = mensaje.attachments
            pregunta.sin_contexto = row["sin_contexto"]
            pregunta.es_administrativa = row["es_administrativa"]

            pregunta.respuestas = self.obtener_respuestas_de_pregunta(pregunta.id_pregunta)    # cargar respuestas asociadas a la pregunta
            preguntas.append(pregunta) # agregar la pregunta a la lista de preguntas abiertas

        return preguntas # devolver la lista de preguntas abiertas

    def obtener_respuestas_de_pregunta(self, id_pregunta):
        """Consulta dinámica a la base de datos para obtener respuestas asociadas a una pregunta específica."""
        # query o consulta a la base de datos para traer respuestas asociadas a una pregunat (pregunta_id) 
        query = """
        SELECT 
            r.id_respuesta, r.texto AS texto_respuesta, r.es_validada, r.es_corta,
            m.id_mensaje, m.id_mensaje_discord, m.contenido, m.fecha_mensaje, m.origen,
            a.id_autor, a.nombre_autor, a.es_docente
        FROM respuestas r
        JOIN mensajes m ON r.mensaje_id = m.id_mensaje
        JOIN autores a ON m.autor_id = a.id_autor
        WHERE r.pregunta_id = %s
        ORDER BY r.orden;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur: # se establece conexión con la base de datos y se crea un cursor para ejecutar la consulta
            cur.execute(query, (id_pregunta,)) # enviar la consulta SQL a la base de datos con el id_pregunta como parámetro
            rows = cur.fetchall() # obtener todas las filas resultantes de la consulta

        respuestas = []
        for row in rows: # iterar sobre cada fila (diccionario) devuelta por la consulta

            autor = Autores(  # construir el autor
                id_autor=row["id_autor"],
                nombre_autor=row["nombre_autor"],
                es_docente=row["es_docente"]
            )

            mensaje = Mensaje( # construir el mensaje de la respuesta
                id_mensaje=row["id_mensaje_discord"],
                autor=autor.nombre_autor,
                contenido=row["texto_respuesta"],
                timestamp=row["fecha_mensaje"].isoformat(),
                attachments=[],
                origen=row["origen"]
            )

            mensaje.id_mensaje_base_de_datos = row["id_mensaje_bd"]

            respuesta = Respuesta(mensaje) # construir la respuesta
            respuesta.es_validada = row["es_validada"]
            respuesta.es_corta = row["es_corta"]

            respuestas.append(respuesta) # agregar la respuesta a la lista de respuestas
        return respuestas
