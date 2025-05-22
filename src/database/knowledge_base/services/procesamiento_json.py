from database.knowledge_base.services.filtros_json import FiltradorContenido
import pandas as pd
from database.knowledge_base.utils.utilidades_logs import guardar_csvs
from database.knowledge_base.services.clase_procesador_mensajes import Procesador
from database.knowledge_base.utils.utilidades_logs import setup_logger

# agregando logger para seguimiento de la carga de datos
logger_proc= setup_logger('carga_procesador','log_procesamiento_con_preguntas_cerradas.txt')

# Función para procesar el archivo JSON y convertirlo a DataFrame
def procesar_json(ruta_json):
    datos = ruta_json.leer_json()
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    return df

# Función para filtrar los mensajes irrelevantes
def aplicar_filtros_mensajes_json(df):

    logger_proc.debug(f" ✉️ Cantidad de mensajes en el json: {len(df)}")
    # Asegurarse de que 'content' exista y convertir a string (por si hay None)
    df["content"] = df["content"].astype(str).str.strip()

    # Filtrar: se queda solo con los que tienen texto real (no vacío)
    df = df[df["content"] != ""]
    logger_proc.debug(f" 🟡 Cantidad de mensajes no vacios: {len(df)}")

    # Filtrar los mensajes irrelevantes visualmente
    visuales_df = df[df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]
    logger_proc.debug(f" 🟡 Cantidad de mensajes irrelevantes como gifs: {len(visuales_df)}")

    # Filtrar DataFrame sin vacios, quitandole los mensajes visuales irrelevantes (emojis, gifs, etc.)
    df = df[~df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]

    # Filtrar los mensajes que tienen solo combinación de números + signos
    sin_numeros_solos_df = df[df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]
    logger_proc.debug(f" 🟡 Cantidad de mensajes con signos raros: {len(sin_numeros_solos_df)}")

    # Filtrar los mensajes que no tengan solo combinación de números + signos
    df = df[~df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]

    # Filtrar los mensajes que tienen solo simbolos
    solo_simbolos_df= df[df["content"].apply(FiltradorContenido.es_solo_simbolos)]
    logger_proc.debug(f" 🟡 Cantidad de mensajes que son solo símbolos: {len(solo_simbolos_df)}")

    # Filtrar los mensajes que no tengan solo combinación de números + signos
    df = df[~df["content"].apply(FiltradorContenido.es_solo_simbolos)]
    logger_proc.debug(f" 🟢 Cantidad de mensajes del json sin vacios, sin gifs y sin simbolos raros: {len(df)}")

    return df, visuales_df, sin_numeros_solos_df,solo_simbolos_df


def procesar_archivos_json(rutas_json):

    procesadores = []  # Lista para guardar cada Procesador

    for idx, ruta_json in enumerate(rutas_json, start=1):
        # Cargar JSON y convertir a DataFrame
        df = procesar_json(ruta_json)
        
        # Obtener nombre base para los archivos
        nombre_base = f"chat_{idx}"
        
        # Filtrar 4 dataframes
              # dataframe con mensajes filtrados. Que los mensajes no sean solo gifs, sticker, emoticones y simbolos
              # dataframe con mensajes que son solo gifs, sticker y emoticones 
              # dataframe con mensajes que sean solo números
              # dataframe con mensajes que sean solo símbolos
        df, visuales_df, sin_numeros_solos_df, solo_simbolos_df = aplicar_filtros_mensajes_json(df)

        # Guardar los dataframes en CSVs para su control visual
        guardar_csvs(df, visuales_df, sin_numeros_solos_df, solo_simbolos_df,nombre_base)

        # Crear procesador de archivo
        nombre_log = f"log_json_{idx:02d}.txt" # se va a tener un log por cada archivo json procesado
        procesador = Procesador(nombre_log)

        # Ordenar dataframe por la columna 'timestamp' de más antiguo a más nuevo (ascendente)
        df = df.sort_values(by='timestamp', ascending=True)

        # se reinicia el índice del Dataframe para que quede ordenado y no haya saltos en los índices
        df = df.reset_index(drop=True)

        # se le pasa a la instancia procesador el Dataframe ya filtrado para la identificación de preguntas y respuestas
        procesador.procesar_dataframe(df,str(ruta_json))

        logger_proc.debug(f"Se tuvieron {procesador.cant_mens_cierre} registros de cierre para el archivo {idx}")

        # se deben guardar los procesadores en una lista ya que se crea uno por cada JSON que se analiza
        procesadores.append(procesador)

        # Registrar resultados del procesamiento
        logger_proc.debug(f" ✅ Procesamiento completado para el archivo {idx}")
        logger_proc.debug(f" 📂 Archivos guardados para el archivo {idx}: {nombre_base}_emojis_gifs_descartados.csv, {nombre_base}_numeros_descartados.csv, {nombre_base}_json_sin_frases_cortas.csv")
        logger_proc.debug(f" 📊 Resultados de procesamiento: {len(procesador.preguntas_abiertas)} preguntas abiertas, {len(procesador.preguntas_cerradas)} preguntas cerradas")
        logger_proc.debug(f" ")
    return procesadores

