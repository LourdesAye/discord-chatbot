from procesamiento_base.procesamiento_base_copy import ProcesadorBase
from estrategias_cierre_mensajes.estrategias_de_cierre_de_menajes import EstrategiaCierreTiempoReal
from psycopg2 import connect, sql, errors
from utils_for_all.conexion_bdd import config
from utils_for_all.utilidades_logs import setup_logger
from psycopg2.extras import RealDictCursor

logger_db_cargada = setup_logger('cargando_datos_desde_bdd', 'log_cargando_datos_desde_base_de_datos_existente.txt')

class ProcesadorTiempoReal(ProcesadorBase):
    # definición explícita solo por claridad del constructor aunque no hace falta
    def __init__(self, nombre_log, estrategias=None):
        # mismos atributos que clase base
        super().__init__(nombre_log, estrategias)
        self.estrategia_cierre = EstrategiaCierreTiempoReal()  # estrategia de cierre para tiempo real
        # se agregan atributos para conexión a base de datos
        self.config = config
        self.conn = self.connect_to_database()


    @property # para que se interprete como atributo y no como método ( self.preguntas_abiertas y no: self.preguntas_abiertas() )
    def preguntas_abiertas(self):
        """Consulta dinámica a la base de datos."""

        return ["Pendiente de implementar"] # debe ser una consulta a la base de datos
        #return Pregunta.obtener_preguntas_abiertas()
    

    def connect_to_database(self):
        """Establece conexión con la base de datos"""
        try:
            conn = connect(
                dbname=self.config["dbname"],
                user=self.config["user"],
                password=self.config["password"],
                host=self.config["host"],
                port=self.config["port"],
            )
            logger_db_cargada.info("Conexión a la base de datos establecida")
            return conn
        except errors.OperationalError as e:
            logger_db_cargada.error(f"Error al conectar a la base de datos: {e}")
            raise
    
    # obtener ultimas dos preguntas cerradas desde la bdd existente
    def obtener_ultimas_dos_preguntas_cerradas(self, nombre_autor):
        # with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
        #     cur.execute("SELECT id_autor FROM autores WHERE nombre_autor = %s", (nombre_autor,))
        #     fila = cur.fetchone()
        #     if fila:
        #         logger_db.debug(f"El autor {nombre_autor} existe en la base de datos")
        #         return fila["id_autor"]
        #     logger_db.debug(f"El autor {nombre_autor} NO existe en la base de datos, se lo va a ingresar")
        #     cur.execute(
        #         """
        #         INSERT INTO autores (nombre_autor, es_docente)
        #         VALUES (%s, %s) RETURNING id_autor
        #         """,
        #         (nombre_autor, self.es_docente(nombre_autor))
        #     )
        #     return cur.fetchone()["id_autor"]
    
    # obtener preguntas abiertas desde la bdd existente
    def insertar_o_obtener_autor(self, nombre_autor):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM preguntas WHERE esta_cerrada = %s", (False,))
            preguntas_abiertas = cur.fetchall()