import pandas as pd
from utils.utilidades_logs import guardar_resultados_en_csvs
from processing.procesamiento_completo import ProcesadorBatch
from utils.utilidades_logs import setup_logger
from utils.filtros_de_mensajes import EstrategiaFiltro,FiltroContenidoIrrelevanteVisual,FiltroSoloNumerosSignos,FiltroSoloSimbolos,FiltroContenidoVacio
from database.models.clase_ruta import Ruta

# agregando logger para seguimiento de la carga de datos
logger_proc= setup_logger('carga_procesador','log_procesamiento_con_preguntas_cerradas.txt')

# Función para procesar el archivo JSON y convertirlo a DataFrame
def cargar_json_como_dataframe(ruta_json : Ruta) -> pd.DataFrame : 
    datos = ruta_json.leer_json() # abre el JSON y lo pasa a un diccionario (par clave-valor)
    mensajes_crudos_df = pd.DataFrame(datos)  # Convierte el diccionario a DataFrame
    return mensajes_crudos_df # devuelve un dataframe (estructura de fila : datos o valor y columna: clave o nombre del atributo) con los datos del json

def aplicar_filtros_mensajes_json(mensajes_crudos_df: pd.DataFrame, filtros_mensajes: list[EstrategiaFiltro]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    logger_proc.debug(f" \n ✉️ Cantidad de mensajes en el json: {len(mensajes_crudos_df)}")
    mensajes_crudos_df["content"] = (mensajes_crudos_df["content"].astype(str).str.strip())
    mensajes_limpios_df = mensajes_crudos_df.copy()
    mensajes_descartados = {}
    for estrategia in filtros_mensajes:
        nombre_filtro = estrategia.nombre()
        mensajes_descartados_df = mensajes_limpios_df[mensajes_limpios_df["content"].apply(estrategia.aplicar)]
        mensajes_descartados[nombre_filtro] = mensajes_descartados_df
        logger_proc.debug( f" 🟡 Cantidad de mensajes filtrados por {nombre_filtro} : {len(mensajes_descartados_df)}")
        mensajes_limpios_df = mensajes_limpios_df[~mensajes_limpios_df["content"].apply(estrategia.aplicar)]
    logger_proc.debug( f" 🟢 Cantidad de mensajes finales luego de todos los filtros:{len(mensajes_limpios_df)}")
    return mensajes_limpios_df, mensajes_descartados

def procesar_archivos_json(rutas_json : list[Ruta]) -> list[ProcesadorBatch]:
    procesadores = []  # Lista para guardar cada Procesador
    for numero_json, ruta_json in enumerate(rutas_json, start=1): # recorre cada directorio
        mensajes_crudos_df = cargar_json_como_dataframe(ruta_json) # Cargar de cada directorio el JSON y lo convierte a DataFrame
        prefijo_archivos_csv = f"chat_{numero_json}"  # Obtener nombre base para los archivos
        filtros_mensajes : list[EstrategiaFiltro]= [ FiltroContenidoVacio(),FiltroContenidoIrrelevanteVisual(), FiltroSoloNumerosSignos(),FiltroSoloSimbolos()]  # definiendo lista de estrategias para aplicar sobre el DataFrame 
        mensajes_limpios_df, mensajes_descartados = aplicar_filtros_mensajes_json(mensajes_crudos_df, filtros_mensajes) # Filtrar 5 dataframes: mensajes con todos los filtros aplicados, con solo mensajes vacios, con mensajes irrelevantes (solo gifs,sticker o emoticón), con mensjaes que son solo número con signo, o mensajes con solo signo
        guardar_resultados_en_csvs(mensajes_limpios_df, mensajes_descartados ,prefijo_archivos_csv)# Guardar los dataframes en CSVs para su control visual
        nombre_log = f"log_json_{numero_json:02d}.txt" # se va a tener un log por cada archivo json procesado

        # ACA VOLVER CUANDO TERMINER DE HACER EL REFACTOR DEL PROCESAMIENTO BATCH Y TIEMPO REAL
        # VER CÓMO SERÁ LA NUEVA INSTANCIACIÓN DEL PROCESADOR
        procesador = ProcesadorBatch(nombre_log) # Crear procesador por cada archivo json procesador
        
        mensajes_limpios_df = mensajes_limpios_df.sort_values(by='timestamp', ascending=True)  # Ordenar dataframe por la columna 'timestamp' de más antiguo a más nuevo (ascendente)
        mensajes_limpios_df = mensajes_limpios_df.reset_index(drop=True)  # se reinicia el índice del Dataframe para que quede ordenado y no haya saltos en los índices
        procesador.procesar_dataframe(mensajes_limpios_df,str(ruta_json)) # se le pasa a la instancia procesador el Dataframe ya filtrado para la identificación de preguntas y respuestas
        procesadores.append(procesador) # se deben guardar los procesadores en una lista ya que se crea uno por cada JSON que se analiza

        # Registrar resultados del procesamiento
        logger_proc.debug(f" ")
        logger_proc.debug(f" \n ✅ Procesamiento completado para el archivo JSON {numero_json}")
        logger_proc.debug(f" 📊 Resultados de procesamiento:")
        logger_proc.debug(f" \n 📊 Análisis de las listas de preguntas una vez finalizado el procesamiento:")
        logger_proc.debug(f"       📊 {len(procesador.preguntas_abiertas)} preguntas abiertas")
        logger_proc.debug(f"       📊 {len(procesador.preguntas_cerradas)} preguntas cerradas")
        logger_proc.debug(f" \n 📊 Análisis de los mensajes procesados:")
        logger_proc.debug(f"       📊 {len(procesador.mensajes_sueltos)} mensajes sueltos")
        logger_proc.debug(f"       📊 {procesador.cant_concatenaciones} mensajes concatenados")
        logger_proc.debug(f"       📊 {procesador.cant_mens_cierre_alumnos} mensajes de cierre de alumnos")
        logger_proc.debug(f"       📊 {procesador.contador_preguntas_nuevas} preguntas generadas")
        logger_proc.debug(f"       📊 {procesador.contador_mensaje_respuesta} mensajes detectados como respuesta")
        logger_proc.debug(f"       ✅ {len(procesador.mensajes_sueltos) + procesador.cant_concatenaciones + procesador.cant_mens_cierre_alumnos + procesador.contador_preguntas_nuevas + procesador.contador_mensaje_respuesta } total de mensajes analizados")
        logger_proc.debug(f"       📊 {procesador.cant_mens_cierre_docente} mensajes detectados como respuesta que también son de cierre de docentes")
        logger_proc.debug(f"       📊 {procesador.cant_mens_cierre_alumnos + procesador.cant_mens_cierre_docente} mensajes totales de cierre (tanto de alumnos como de docentes)")
        if len(procesador.mensajes_sueltos) >=1:
            for indice,mensaje_suelto in enumerate(procesador.mensajes_sueltos,start=1):
                logger_proc.debug(f" \n✉️ Listado de mensajes sueltos: ")
                logger_proc.debug(f" ✉️ El mensaje suelto {indice}: \n'{mensaje_suelto.contenido}'")
        logger_proc.debug(f" ")
    return procesadores

