import pandas as pd
from utils_for_all.utilidades_logs import guardar_resultados_en_csvs
from database.knowledge_base.services.clase_procesador_mensajes import Procesador
from utils_for_all.utilidades_logs import setup_logger
from database.knowledge_base.services.filtros_json import FiltroContenidoIrrelevanteVisual,FiltroSoloNumerosSignos,FiltroSoloSimbolos,FiltroContenidoVacio

# agregando logger para seguimiento de la carga de datos
logger_proc= setup_logger('carga_procesador','log_procesamiento_con_preguntas_cerradas.txt')
logger_mensajes_sueltos = setup_logger('mensajes_sueltos','log_mensajes_sueltos')

# Función para procesar el archivo JSON y convertirlo a DataFrame
def procesar_json(ruta_json):
    datos = ruta_json.leer_json() # abre el JSON y lo pasa a un diccionario (pra clave-valor)
    df = pd.DataFrame(datos)  # Convierte el diccionario a DataFrame
    return df # devueñlve un dataframe (estructura de fila : datos o valor y columna: clave o nombre del atributo) con los datos del json

# Función oara aplicar las estrategias (filtros o algoritmos) en el dataframe
def aplicar_filtros_mensajes_json(df, estrategias):
    logger_proc.debug(f" ✉️ Cantidad de mensajes en el json: {len(df)}") # para mantener la trazabilidad de la cantidad de registros que se analizan
    df["content"] = df["content"].astype(str).str.strip() # asegura que valor de esa columna content sea string y quita espacios vacios al inicio y al final
    mensajes_filtrados = {} # para tener un diccionario de dataframes que se obtienen por cada filtro aplicado
    for estrategia in estrategias: # estartegia es cada uno de los filtros que se aplican al dataframe
        nombre = estrategia.nombre() # se capta nombre de la estrategia para que sea la clave del diccionario junto con su dataframe filtrado
        filtrados_df = df[df["content"].apply(estrategia.aplicar)] # se aplica el filtro en la columna content del dataframe
        mensajes_filtrados[nombre] = filtrados_df # se asocia el dataframe filtrado(valor) con el nombre de la estrategia(clave)
        logger_proc.debug(f" 🟡 Cantidad de mensajes filtrados por '{nombre}': {len(filtrados_df)}") # para trazabilidad de mensajes filtrados de acuerdo a la estrategia
        df = df[~df["content"].apply(estrategia.aplicar)] # al dataframe base se le quitan los registros que fueron filtrados (no deseados)
    logger_proc.debug(f" 🟢 Cantidad de mensajes finales luego de todos los filtros: {len(df)}") # trazabilidad de cada filtro aplicado a los registros
    return df, mensajes_filtrados # devuelve el dataframe a procesar y los dataframes filtrados (con los registros indeseables)

def procesar_archivos_json(rutas_json):
    procesadores = []  # Lista para guardar cada Procesador
    for idx, ruta_json in enumerate(rutas_json, start=1): # recorre cada directorio
        df = procesar_json(ruta_json) # Cargar de cada directorio el JSON y lo convierte a DataFrame
        nombre_base = f"chat_{idx}"  # Obtener nombre base para los archivos
        estrategias = [ FiltroContenidoVacio(),FiltroContenidoIrrelevanteVisual(), FiltroSoloNumerosSignos(),FiltroSoloSimbolos()]  # definiendo lista de estrategias para aplicar sobre el DataFrame 
        df, filtrados = aplicar_filtros_mensajes_json(df, estrategias) # Filtrar 5 dataframes: mensajes con todos los filtros aplicados, con solo mensajes vacios, con mensajes irrelevantes (solo gifs,sticker o emoticón), con mensjaes que son solo número con signo, o mensajes con solo signo
        guardar_resultados_en_csvs(df, filtrados ,nombre_base)# Guardar los dataframes en CSVs para su control visual
        nombre_log = f"log_json_{idx:02d}.txt" # se va a tener un log por cada archivo json procesado
        procesador = Procesador(nombre_log) # Crear procesador por cada archivo json procesado
        df = df.sort_values(by='timestamp', ascending=True)  # Ordenar dataframe por la columna 'timestamp' de más antiguo a más nuevo (ascendente)
        df = df.reset_index(drop=True)  # se reinicia el índice del Dataframe para que quede ordenado y no haya saltos en los índices
        procesador.procesar_dataframe(df,str(ruta_json)) # se le pasa a la instancia procesador el Dataframe ya filtrado para la identificación de preguntas y respuestas
        procesadores.append(procesador) # se deben guardar los procesadores en una lista ya que se crea uno por cada JSON que se analiza

        # Registrar resultados del procesamiento
        logger_proc.debug(f" ")
        logger_proc.debug(f" ✅ Procesamiento completado para el archivo {idx}")
        logger_proc.debug(f" 📊 Resultados de procesamiento:")
        logger_proc.debug(f"       📊 {len(procesador.mensajes_sueltos)} mensajes sueltos")
        logger_proc.debug(f"       📊 {procesador.cant_concatenaciones} mensajes concatenados")
        logger_proc.debug(f"       📊 {procesador.cant_mens_cierre_alumnos} mensajes de cierre de alumnos")
        logger_proc.debug(f"       📊 {procesador.contador_preguntas_nuevas} preguntas generadas")
        logger_proc.debug(f"       📊 {procesador.contador_mensaje_respuesta} mensajes detectados como respuesta")
        logger_proc.debug(f"       ✅ {len(procesador.mensajes_sueltos) + procesador.cant_concatenaciones + procesador.cant_mens_cierre_alumnos + procesador.contador_preguntas_nuevas + procesador.contador_mensaje_respuesta } total de mensajes analizados")
        logger_proc.debug(f"       📊 {procesador.cant_mens_cierre_docente} mensajes de cierre de docentes")
        logger_proc.debug(f"       📊 {len(procesador.preguntas_abiertas)} preguntas abiertas")
        logger_proc.debug(f" ")

        logger_mensajes_sueltos.debug(f" ✅ Procesamiento completado para el archivo JSON {idx}")
        logger_mensajes_sueltos.debug(f" 📊 {procesador.cant_mens_cierre_alumnos} mensajes de cierre de alumnos")
        logger_mensajes_sueltos.debug(f" 📊 {procesador.cant_mens_cierre_docente} mensajes de cierre de docentes")
        logger_mensajes_sueltos.debug(f" 📊 {procesador.cant_mens_cierre_alumnos + procesador.cant_mens_cierre_docente} mensajes totales de cierre (tanto de alumnos como de docentes) para el archivo {idx}")
        logger_mensajes_sueltos.debug(f" ✅ Cantidad de mensajes sueltos detectados: {len(procesador.mensajes_sueltos)}")
        if len(procesador.mensajes_sueltos) >=1:
            for indice,mensaje_suelto in enumerate(procesador.mensajes_sueltos,start=1):
                logger_mensajes_sueltos.debug(f" ✉️ Mostrando mensajes sueltos...")
                logger_mensajes_sueltos.debug(f" ✉️ El mensaje suelto {indice}: '{mensaje_suelto.contenido}'")
        logger_mensajes_sueltos.debug(f" ")
    return procesadores

