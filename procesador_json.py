import pandas as pd
import json
import re
import os
from datetime import datetime, timedelta
from clase_procesador_mensajes import Procesador
from clase_cargar_bdd import GestorBD
from utilidades_logs import setup_logger

# agregando logger para seguimiento de la carga de datos
logger_proc= setup_logger('carga_procesador','log_carga_de_procesador_con_preguntas_cerradas.txt')

# Clase para Filtrado de Contenidos
class FiltradorContenido:
    @staticmethod
    def es_contenido_irrelevante_visual(texto):
        texto = texto.strip().lower()
        solo_emojis = re.fullmatch(r"[\s\U0001F300-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+", texto)
        es_link_tenor_giphy = re.fullmatch(r"(https?:\/\/)?(www\.)?(tenor|giphy)\.com\S*", texto)
        es_sticker_gif = texto in {"sticker", "gif"}
        return bool(solo_emojis or es_link_tenor_giphy or es_sticker_gif)

    @staticmethod
    def es_solo_numeros_signos(texto):
        return bool(re.fullmatch(r"[+\d\s]+", texto))


# Función para procesar el archivo JSON y convertirlo a DataFrame
def procesar_json(ruta_json):
    with open(ruta_json, "r", encoding="utf-8") as f:
        datos = json.load(f)
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    return df


# Función para filtrar los mensajes irrelevantes
def filtrar_mensajes(df):

    logger_proc.debug(f" cantidad de mensajes en el json: {len(df)}")
    # Asegurarse de que 'content' exista y convertir a string (por si hay None)
    df["content"] = df["content"].astype(str).str.strip()

    # Filtrar: se queda solo con los que tienen texto real (no vacío)
    df = df[df["content"] != ""]
    logger_proc.debug(f"cantidad de mensajes no vacios: {len(df)}")

    # Filtrar los mensajes irrelevantes visualmente
    visuales_df = df[df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]
    logger_proc.debug(f"cantidad de mensajes irrelevantes como gifs: {len(visuales_df)}")

    # Filtrar DataFrame sin vacios, quitandole los mensajes visuales irrelevantes (emojis, gifs, etc.)
    df = df[~df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]
    logger_proc.debug(f"cantidad de mensajes del json sin irrelevantes como gifs: {len(df)}")

    # Filtrar los mensajes que tienen solo combinación de números + signos
    sin_numeros_solos_df = df[df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]
    logger_proc.debug(f"cantidad de mensajes con signos raros: {len(sin_numeros_solos_df)}")

    # Filtrar los mensajes que no tengan solo combinación de números + signos
    df = df[~df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]
    logger_proc.debug(f"cantidad de mensajes del json sin vacios, sin gifs y sin simbolos raros: {len(df)}")

    return df, visuales_df, sin_numeros_solos_df


# Función para guardar los CSVs con los resultados
def guardar_csvs(df, visuales_df, sin_numeros_solos_df, nombre_base):
    visuales_df[["content"]].to_csv(f"{nombre_base}_emojis_gifs_descartados.csv", index=False, encoding="utf-8")
    sin_numeros_solos_df[["content"]].to_csv(f"{nombre_base}_numeros_descartados.csv", index=False, encoding="utf-8")
    df[["content"]].to_csv(f"{nombre_base}_json_limpio.csv", index=False, encoding="utf-8")


# Función principal para procesar los JSONs
def procesar_archivos_json(rutas_json):

    procesadores = []  # Lista para guardar cada Procesador

    for idx, ruta_json in enumerate(rutas_json, start=1):
        # Cargar JSON y convertir a DataFrame
        df = procesar_json(ruta_json)
        
        # Obtener nombre base para los archivos
        nombre_base = f"chat_{idx}"
        
        # Filtrar los mensajes
        df, visuales_df, sin_numeros_solos_df = filtrar_mensajes(df)

        # Guardar los CSVs
        guardar_csvs(df, visuales_df, sin_numeros_solos_df, nombre_base)

        # Crear procesador y procesar los mensajes
        procesador = Procesador()
        # Ordenar por la columna 'timestamp' en orden ascendente (si querés descendente poné 'False')
        df = df.sort_values(by='timestamp', ascending=True)
        # Reiniciar el índice para que quede ordenado y no haya saltos en los índices
        df = df.reset_index(drop=True)
        procesador.procesar_dataframe(df,ruta_json)
        procesadores.append(procesador)
        # Mostrar resultados del procesamiento
        logger_proc.debug(f"✅ Procesamiento completado para el archivo {idx}")
        logger_proc.debug(f"📂 Archivos guardados para el archivo {idx}: {nombre_base}_emojis_gifs_descartados.csv, {nombre_base}_numeros_descartados.csv, {nombre_base}_json_sin_frases_cortas.csv")
        logger_proc.debug(f"📊 Resultados de procesamiento: {len(procesador.preguntas_abiertas)} preguntas abiertas, {len(procesador.preguntas_cerradas)} preguntas cerradas")
        logger_proc.debug(f" ")
    return procesadores

# Rutas a los archivos JSON
rutas_json = [
    r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1221091721383903262\chat.json",
    r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1219817856288686083\chat.json",
    r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1221091674248446003\chat.json"
]


# Llamar a la función principal para procesar todos los archivos JSON
procesadores = procesar_archivos_json(rutas_json)
logger_proc.debug(f"🔍 Cantidad de procesadores generados: {len(procesadores)}")

config = {
    "dbname": "base_de_conocimiento_chatbot",
    "user": "postgres",
    "password": "0909casajardinpaz0707",
    "host": "localhost",
    "port": "5432",
    "docentes": [
        "ezequieloescobar", "aylenmsandoval",
        "lucassaclier", "facuherrera_8", "ryan129623"
    ]
}

logger_proc.debug("🗃️ Conectándose a la base de datos...")
bd = GestorBD(config)
logger_proc.debug("vas a ingresar a la posible carga de datos")

total_reg_resp = 0
total_reg_preguntas =0
total_reg_adj_preg = 0
total_reg_adj_resp= 0

# Persistir preguntas de todos los procesadores
for index,proc in enumerate(procesadores,start=1):
    total_reg_preguntas=total_reg_preguntas + len(proc.preguntas_cerradas)
    logger_proc.debug(f" ")
    logger_proc.debug(f"analizando el json número : {index}")
    logger_proc.debug(f"Cantidad de Preguntas Cerradas {len(proc.preguntas_cerradas)}")
    cant_resp= 0
    for index,pregunta in enumerate(proc.preguntas_cerradas,start=1):
        #logger_proc.debug(f"La pregunta {index} posee {len(pregunta.respuestas)} respuestas")
        cant_resp=cant_resp+len(pregunta.respuestas)
        total_reg_adj_preg=total_reg_adj_preg + len(pregunta.attachments)
        for respuesta in pregunta.respuestas:
            total_reg_adj_resp=total_reg_resp+ len(respuesta.attachments)
    total_reg_resp = total_reg_resp + cant_resp
    logger_proc.debug(f"La cantidad total de respuestas en el json {index} es {cant_resp}")
    #bd.persistir_preguntas(proc.preguntas_cerradas)

logger_proc.debug(f"La cantidad total de preguntas : {total_reg_preguntas}")
logger_proc.debug(f"La cantidad total de respuestas: {total_reg_resp}")
logger_proc.debug(f"La cantidad total archivos adjuntos de preguntas : {total_reg_adj_preg}")
logger_proc.debug(f"La cantidad total archivos adjuntos de respuestas : {total_reg_adj_resp}")

bd.cerrar_conexion()
logger_proc.debug("💾 Conexión cerrada y datos guardados.")

