from database.models.clase_mensajes import Mensaje
from database.models.clase_preguntas import Pregunta
from utils.utilidades_logs import setup_logger

logger_db_cargada = setup_logger('actualizando_datos_en_bdd', 'log_actualizando_base_de_datos_en_realtime.txt')

# Para evitar condición de carrera (dos procesos o hilos acceden o modifican al mismo tiempo un mismo dato en la base)
# Antes de cerrar una pregunta, verificar que nadie más la haya cerrado
# Esto evita sobreescribir un cambio que ya se hizo.
# Esto se llama optimistic locking (bloqueo optimista (con chequeo previo))
# PostgreSQL actualiza la fila solo si sigue abierta, y devuelve cuántas filas afectó.
# Si rowcount es 0, alguien más la cambió antes.

class EstrategiaCierre:
    def cerrar(self, pregunta: Pregunta, mensaje: Mensaje, motivo: str):
        raise NotImplementedError("Debes implementar el método cerrar")

class EstrategiaCierreBatch(EstrategiaCierre):
    def __init__(self, procesador):
        self.procesador = procesador  # Para acceder a preguntas_abiertas, etc.

    def cerrar(self, pregunta: Pregunta, mensaje: Mensaje, motivo: str):
        """Cierra una pregunta en el contexto del procesamiento por lotes."""
        pregunta.cerrar() # se marca la pregunta como cerrada
        self.procesador.registrar_cierre(pregunta, motivo) 

class EstrategiaCierreTiempoReal(EstrategiaCierre):

    def cerrar(self, pregunta: Pregunta, mensaje: Mensaje, motivo: str):
        """Cierra una pregunta en la base de datos de forma segura."""
        query = """
        UPDATE preguntas
        SET esta_cerrada = TRUE
        WHERE id_pregunta = %s AND esta_cerrada = FALSE;
        """

        try:
            with self.conn: # with para atomicidad, todo el código dentro del bloque se ejecuta sin errores, se hace commit, caso contrario rollback. 
                with self.conn.cursor() as cur: # para que cursor se cierre automáticamente al salir del bloque with
                    cur.execute(query, (pregunta.id_pregunta,)) 
                    if cur.rowcount == 0: # si no se actualizó ninguna fila, significa que la pregunta ya estaba cerrada
                        logger_db_cargada.warning( f"⚠️ La pregunta {pregunta.id_pregunta} ya fue cerrada por otro proceso.")
                        return False
                    logger_db_cargada.info(
                        f"🟢 Pregunta {pregunta.id_pregunta} cerrada correctamente (motivo: {motivo})."
                    )
                    return True
        except Exception as e:
            logger_db_cargada.error(
                f"❌ Error al cerrar la pregunta {pregunta.id_pregunta}: {e}"
            )
            return False