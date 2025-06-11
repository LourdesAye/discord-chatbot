import pandas as pd
from utils_for_all.utilidades_logs import guardar_csvs
from database.knowledge_base.services.clase_procesador_mensajes import Procesador
from utils_for_all.utilidades_logs import setup_logger
from database.knowledge_base.services.filtros_json import FiltroContenidoIrrelevanteVisual,FiltroSoloNumerosSignos,FiltroSoloSimbolos,FiltroContenidoVacio

# agregando logger para seguimiento de la carga de datos
logger_proc= setup_logger('carga_procesador','log_procesamiento_con_preguntas_cerradas.txt')
logger_mensajes_sueltos = setup_logger('mensajes_sueltos','log_mensajes_sueltos')

# Función para procesar el archivo JSON y convertirlo a DataFrame
def procesar_json(ruta_json):
    datos = ruta_json.leer_json()
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    return df

# # Función para filtrar los mensajes irrelevantes
# def aplicar_filtros_mensajes_json(df):

#     logger_proc.debug(f" ✉️ Cantidad de mensajes en el json: {len(df)}")
#     # Asegurarse de que 'content' exista y convertir a string (por si hay None)
#     df["content"] = df["content"].astype(str).str.strip()

#     # Filtrar: se queda solo con los que tienen texto real (no vacío)
#     df = df[df["content"] != ""]
#     logger_proc.debug(f" 🟡 Cantidad de mensajes no vacios: {len(df)}")

#     # Filtrar los mensajes irrelevantes visualmente
#     visuales_df = df[df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]
#     logger_proc.debug(f" 🟡 Cantidad de mensajes irrelevantes como gifs: {len(visuales_df)}")

#     # Filtrar DataFrame sin vacios, quitandole los mensajes visuales irrelevantes (emojis, gifs, etc.)
#     df = df[~df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]

#     # Filtrar los mensajes que tienen solo combinación de números + signos
#     sin_numeros_solos_df = df[df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]
#     logger_proc.debug(f" 🟡 Cantidad de mensajes con signos raros: {len(sin_numeros_solos_df)}")

#     # Filtrar los mensajes que no tengan solo combinación de números + signos
#     df = df[~df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]

#     # Filtrar los mensajes que tienen solo simbolos
#     solo_simbolos_df= df[df["content"].apply(FiltradorContenido.es_solo_simbolos)]
#     logger_proc.debug(f" 🟡 Cantidad de mensajes que son solo símbolos: {len(solo_simbolos_df)}")

#     # Filtrar los mensajes que no tengan solo combinación de números + signos
#     df = df[~df["content"].apply(FiltradorContenido.es_solo_simbolos)]
#     logger_proc.debug(f" 🟢 Cantidad de mensajes del json sin vacios, sin gifs y sin simbolos raros: {len(df)}")

#     return df, visuales_df, sin_numeros_solos_df,solo_simbolos_df

# def aplicar_filtros_mensajes_json(df):
#     logger_proc.debug(f" ✉️ Cantidad de mensajes en el json: {len(df)}")

#     # Accede a la columna llamada "content" del DataFrame df. Esto devuelve una Serie de pandas.
#     # Convierte todos los valores de la columna a cadena de texto
#     # Se eliminan los espacios al inicio y al final de cada texto
#     # El resultado se guarda nuevamente en la misma columna, sobrescribiendo su contenido
#     df["content"] = df["content"].astype(str).str.strip()
   
#     # Instanciar estrategias
#     estrategia_vacios = FiltroContenidoVacio()
#     estrategia_visual = FiltroContenidoIrrelevanteVisual()
#     estrategia_signos = FiltroSoloNumerosSignos()
#     estrategia_simbolos = FiltroSoloSimbolos()

#     # Aplicar filtros

#     df_vacios = df[df["content"].aply(estrategia_vacios.aplicar)]
#     logger_proc.debug(f" 🟡 Cantidad de mensajes vacíos: {len(df_vacios)}")
#     df = df[~df["content"].aply(estrategia_vacios.aplicar)]

#     visuales_df = df[df["content"].apply(estrategia_visual.aplicar)]
#     logger_proc.debug(f" 🟡 Cantidad de mensajes irrelevantes como gifs: {len(visuales_df)}")
#     df = df[~df["content"].apply(estrategia_visual.aplicar)]

#     sin_numeros_solos_df = df[df["content"].apply(estrategia_signos.aplicar)]
#     logger_proc.debug(f" 🟡 Cantidad de mensajes con signos raros: {len(sin_numeros_solos_df)}")
#     df = df[~df["content"].apply(estrategia_signos.aplicar)]

#     solo_simbolos_df = df[df["content"].apply(estrategia_simbolos.aplicar)]
#     logger_proc.debug(f" 🟡 Cantidad de mensajes que son solo símbolos: {len(solo_simbolos_df)}")
#     df = df[~df["content"].apply(estrategia_simbolos.aplicar)]

#     logger_proc.debug(f" 🟢 Cantidad final de mensajes limpios: {len(df)}")

#     return df, visuales_df, sin_numeros_solos_df, solo_simbolos_df

def aplicar_filtros_mensajes_json(df, estrategias):
    import logging
    logger_proc = logging.getLogger("procesamiento")

    logger_proc.debug(f" ✉️ Cantidad de mensajes en el json: {len(df)}")

    df["content"] = df["content"].astype(str).str.strip()

    mensajes_filtrados = {} # diccionario de dataframes

    for estrategia in estrategias:
        nombre = estrategia.nombre()
        filtrados_df = df[df["content"].apply(estrategia.aplicar)]
        mensajes_filtrados[nombre] = filtrados_df
        logger_proc.debug(f" 🟡 Cantidad de mensajes filtrados por '{nombre}': {len(filtrados_df)}")
        df = df[~df["content"].apply(estrategia.aplicar)]

    logger_proc.debug(f" 🟢 Cantidad de mensajes finales luego de todos los filtros: {len(df)}")

    return df, mensajes_filtrados

def procesar_archivos_json(rutas_json):

    procesadores = []  # Lista para guardar cada Procesador

    for idx, ruta_json in enumerate(rutas_json, start=1):
        # Cargar JSON y convertir a DataFrame
        df = procesar_json(ruta_json)
        
        # Obtener nombre base para los archivos
        nombre_base = f"chat_{idx}"

        # definiendo lista de estrategias para aplicar sobre el DataFrame
        estrategias = [
            FiltroContenidoVacio(),
            FiltroContenidoIrrelevanteVisual(),
            FiltroSoloNumerosSignos(),
            FiltroSoloSimbolos()
        ]
        
        # Filtrar 5 dataframes
              # dataframe con mensajes filtrados. Que los mensajes no sean solo gifs, sticker, emoticones y simbolos
              # dataframe con mensajes vacios
              # dataframe con mensajes que son solo gifs, sticker y emoticones 
              # dataframe con mensajes que sean solo números
              # dataframe con mensajes que sean solo símbolos
        df, filtrados = aplicar_filtros_mensajes_json(df, estrategias)
        # Acceder a los DataFrames filtrados:
        df_vacios = filtrados["vacio"]
        df_gifs = filtrados["irrelevante_visual"]
        df_signos = filtrados["solo_numeros_signos"]
        df_simbolos = filtrados["solo_simbolos"]

        # Guardar los dataframes en CSVs para su control visual
        guardar_csvs(df,df_vacios, df_gifs, df_signos,df_simbolos,nombre_base)

        # Crear procesador de archivo
        nombre_log = f"log_json_{idx:02d}.txt" # se va a tener un log por cada archivo json procesado
        procesador = Procesador(nombre_log)

        # Ordenar dataframe por la columna 'timestamp' de más antiguo a más nuevo (ascendente)
        df = df.sort_values(by='timestamp', ascending=True)
        # se reinicia el índice del Dataframe para que quede ordenado y no haya saltos en los índices
        df = df.reset_index(drop=True)

        # se le pasa a la instancia procesador el Dataframe ya filtrado para la identificación de preguntas y respuestas
        procesador.procesar_dataframe(df,str(ruta_json))

        # se deben guardar los procesadores en una lista ya que se crea uno por cada JSON que se analiza
        procesadores.append(procesador)

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

