from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_preguntas import Pregunta
from utils_for_all.utilidades_logs import setup_logger

logger_db_cargada = setup_logger('actualizando_datos_en_bdd', 'log_actualizando_base_de_datos_en_realtime.txt')

# Para evitar condición de carrera (dos procesos o hilos acceden o modifican al mismo tiempo un mismo dato en la base.)  Bloqueos optimistas (con chequeo previo)

# Antes de cerrar una pregunta, podés verificar que nadie más la haya cerrado 🟢 Esto evita sobreescribir un cambio que ya se hizo.
# PostgreSQL actualiza la fila solo si sigue abierta, y te devuelve cuántas filas afectó.
# Si rowcount es 0, alguien más la cambió antes.

# Esto se llama optimistic locking (bloqueo optimista).

class EstrategiaCierre:
    def cerrar(self, pregunta: Pregunta, mensaje: Mensaje, motivo: str):
        raise NotImplementedError("Debes implementar el método cerrar")

class EstrategiaCierreBatch(EstrategiaCierre):
    def __init__(self, procesador):
        self.procesador = procesador  # Para acceder a preguntas_abiertas, etc.

    def cerrar(self, pregunta: Pregunta, mensaje: Mensaje, motivo: str):
        """Cierra una pregunta en el contexto del procesamiento por lotes."""
        pregunta.cerrar() # se marca la pregunta como cerrada
        self.procesador.registrar_cierre(pregunta, motivo) # elimina la pregunta de la lista de preguntas_abiertas y la mueve a lista de preguntas_cerradas, que están en memoria, 

class EstrategiaCierreTiempoReal(EstrategiaCierre):

    def cerrar(self, pregunta: Pregunta, mensaje: Mensaje, motivo: str):
        """Cierra una pregunta en la base de datos de forma segura."""
        query = """
        UPDATE preguntas
        SET esta_cerrada = TRUE
        WHERE id_pregunta = %s AND esta_cerrada = FALSE;
        """
        
        # Bloqueo optimista (optimistic locking) (con chequeo previo). 
            # para manejar situaciones en las que dos o más procesos o hilos 
            # acceden o modifican al mismo tiempo un mismo dato en la base de datos
            # a esa situación se la denomina condición de carrera
            
            # técnica de control de concurrencia que evita el uso de bloqueos físicos durante una transacción, 
            # asumiendo que los conflictos entre transacciones son poco frecuentes.  
            # Se parte de la idea de que dos transacciones no modificarán la misma fila al mismo tiempo.
            # No se bloquea la fila al leerla, con un campos con un estado original (por ejemplo, version, estado, esta_cerrada, etc).
            #  Antes de escribir, el sistema verifica si la fila fue modificada por otra transacción. 
                # Si cambió, se aborta o se reintenta. 
            
            # En este caso: 
            # Se intenta cerrar una pregunta (poner esta_cerrada = TRUE)
                # antes de cambiar, se verifica que la pregunta no esté cerrada (where esta_cerrada= FALSE). 
                    # (no se bloquea la fila al leerla).
                # Si otra transacción la hubiera cerrado, la consulta no afectará ninguna fila (y rowcount será 0).
                # Si rowcount es 0, significa que alguien más la cerró antes, y no se hace ningún cambio.
        

        try:
            with self.conn: 
                # con el with se asegura la atomicidad, es decir, se inicia una transacción: 
                    # si todo el código dentro del bloque with se ejecuta sin errores, se hace automáticamente un commit. 
                    # Si ocurre una excepción, se hace automáticamente un rollback. 
                        # no se necesita poner manualmente conn.commit() y con.rollback(), evitando errores (más seguridad) de olvidos
                with self.conn.cursor() as cur: # esto es para que el cursor se cierre automáticamente al salir del bloque with
                        # el cursor es un objeto que permite ejecutar consultas y obtener resultados
                    cur.execute(query, (pregunta.id_pregunta,)) # ejecutar la consulta con el id de la pregunta
                        # el segundo parámetro es una tupla con los valores para los placeholders (%s)
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

# TEMPORALMENTE SE DEJA ASÍ:
    # los return sirven para comunicar al código que llamó a cerrar() si la operación:
        # se ejecutó correctamente (True → la pregunta se cerró);
        # falló o ya estaba cerrada (False).
    # Esto puede ser útil, si más adelante se quiere:
        # Registrar una acción adicional solo si la pregunta se cerró con éxito.
        # Reintentar el cierre en caso de error.
        # Mostrar un mensaje en logs o en el bot según el resultado.