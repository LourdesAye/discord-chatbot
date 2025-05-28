from database.knowledge_base.data_base.conexion_bdd import config
from database.knowledge_base.services.analizador_preguntas_cerradas import AnalizadorPreguntasCerradas
from database.knowledge_base.data_base.clase_cargar_bdd import GestorBD
from database.knowledge_base.config.admin_rutas import rutas_json
from database.knowledge_base.services.procesamiento_json import procesar_archivos_json
from database.knowledge_base.utils.utilidades_logs import setup_logger

# LOGGER para seguimiento de la carga de datos
logger_proc= setup_logger('carga_procesador','log_procesamiento_con_preguntas_cerradas.txt')

# PROCESAMIENTO de los JSONs y PERSISTENCIA de DATOS
procesadores = procesar_archivos_json(rutas_json) # función para procesar todos los archivos JSON
logger_proc.debug(f" 🔍 Cantidad de procesadores generados: {len(procesadores)}")
logger_proc.debug(" 🗃️ Conectándose a la base de datos...") 

bd = GestorBD(config) # configuración y conexión con BDD

cant_total_resp = 0 # contador de respuestas de todos los json
cant_total_preg =0 # contador de preguntas de todos los json

for indice,proc in enumerate(procesadores,start=1): # por cada procesador 
    analizador = AnalizadorPreguntasCerradas(proc.preguntas_cerradas)
    #s e aplica analisis de preguntas sin contexto, preguntas administrativas y respuestas validadas
    cantidad_preguntas_json, cantidad_respuestas_json, preguntas_a_procesar = analizador.aplicar_analisis_preguntas(indice)
    # contador de preguntas y respuestas que va acumulando por cada json
    cant_total_preg = cant_total_preg + cantidad_preguntas_json
    cant_total_resp = cant_total_resp + cantidad_respuestas_json
    # persistencia de datos de la lista de preguntas cerradas con el analisis aplicado
    bd.persistir_preguntas(preguntas_a_procesar,indice)

logger_proc.debug(f" ")
logger_proc.debug(f" ✅ La cantidad total de preguntas generadas : {cant_total_preg}")
logger_proc.debug(f" ✅ La cantidad total de respuestas generadas : {cant_total_resp}")
bd.cerrar_conexion() # cerrar conexión con bdd
logger_proc.debug(f" ")
logger_proc.debug(" 💾 Conexión cerrada y datos guardados.")

def main():
    logger_proc.debug("Ejecutando main.py")

if __name__ == "__main__":
    main()

