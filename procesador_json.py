import pandas as pd
import json
import re
import os
from datetime import datetime, timedelta
from main.clase_procesador_mensajes import Procesador
from main.clase_cargar_bdd import GestorBD
from utilidades.utilidades_logs import setup_logger
from main.admin_rutas import rutas_json
from main.clase_autores import docentes

# ------------------------------------------------- LOGGER -------------------------------------------------------------#
# agregando logger para seguimiento de la carga de datos
logger_proc= setup_logger('carga_procesador','log_carga_de_procesador_con_preguntas_cerradas.txt')


# -------------------- FILTRADO DE MENSAJES VACIOS,CON GIF, EMOTICON, GIF, SIMBOLOS CON NUMEROS -----------------------#

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
    
    @staticmethod
    def es_solo_simbolos(texto):
        texto = texto.strip()
        # Si no contiene letras ni números
        return not re.search(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]', texto)


# Función para procesar el archivo JSON y convertirlo a DataFrame
def procesar_json(ruta_json):

    datos = ruta_json.leer_json()
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    return df


# Función para filtrar los mensajes irrelevantes
def filtrar_mensajes(df):

    logger_proc.debug(f" Cantidad de mensajes en el json: {len(df)}")
    # Asegurarse de que 'content' exista y convertir a string (por si hay None)
    df["content"] = df["content"].astype(str).str.strip()

    # Filtrar: se queda solo con los que tienen texto real (no vacío)
    df = df[df["content"] != ""]
    logger_proc.debug(f"Cantidad de mensajes no vacios: {len(df)}")

    # Filtrar los mensajes irrelevantes visualmente
    visuales_df = df[df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]
    logger_proc.debug(f"Cantidad de mensajes irrelevantes como gifs: {len(visuales_df)}")

    # Filtrar DataFrame sin vacios, quitandole los mensajes visuales irrelevantes (emojis, gifs, etc.)
    df = df[~df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]

    # Filtrar los mensajes que tienen solo combinación de números + signos
    sin_numeros_solos_df = df[df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]
    logger_proc.debug(f"Cantidad de mensajes con signos raros: {len(sin_numeros_solos_df)}")

    # Filtrar los mensajes que no tengan solo combinación de números + signos
    df = df[~df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]

    # Filtrar los mensajes que tienen solo simbolos
    solo_simbolos_df= df[df["content"].apply(FiltradorContenido.es_solo_simbolos)]
    logger_proc.debug(f"Cantidad de mensajes que son solo símbolos: {len(solo_simbolos_df)}")

    # Filtrar los mensajes que no tengan solo combinación de números + signos
    df = df[~df["content"].apply(FiltradorContenido.es_solo_simbolos)]
    logger_proc.debug(f"Cantidad de mensajes del json sin vacios, sin gifs y sin simbolos raros: {len(df)}")

    return df, visuales_df, sin_numeros_solos_df,solo_simbolos_df


# Función para guardar los CSVs con los resultados
def guardar_csvs(df, visuales_df, sin_numeros_solos_df, solo_simbolos_df,nombre_base):
    visuales_df[["content"]].to_csv(f"{nombre_base}_emojis_gifs_descartados.csv", index=False, encoding="utf-8")
    sin_numeros_solos_df[["content"]].to_csv(f"{nombre_base}_numeros_descartados.csv", index=False, encoding="utf-8")
    solo_simbolos_df[["content"]].to_csv(f"{nombre_base}_simbolos_descartados.csv", index=False, encoding="utf-8")
    df[["content"]].to_csv(f"{nombre_base}_json_limpio.csv", index=False, encoding="utf-8")

#-------------------------------------------Función de PROCESAMIENTO-------------------------------------------------------#
#  Función principal para procesar los JSONs
def procesar_archivos_json(rutas_json):

    procesadores = []  # Lista para guardar cada Procesador

    for idx, ruta_json in enumerate(rutas_json, start=1):
        # Cargar JSON y convertir a DataFrame
        df = procesar_json(ruta_json)
        
        # Obtener nombre base para los archivos
        nombre_base = f"chat_{idx}"
        
        # Filtrar 3 dataframes
              # dataframe con mensajes que no sean solo gifs, sticker, emoticones y simbolos como +1
              # dataframe con mensajes que son solo gifs, sticker y emoticones 
              # dataframe con mensjaes que son solo simbolos más numero como +1
        df, visuales_df, sin_numeros_solos_df, solo_simbolos_df = filtrar_mensajes(df)

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
        logger_proc.debug(f"✅ Procesamiento completado para el archivo {idx}")
        logger_proc.debug(f"📂 Archivos guardados para el archivo {idx}: {nombre_base}_emojis_gifs_descartados.csv, {nombre_base}_numeros_descartados.csv, {nombre_base}_json_sin_frases_cortas.csv")
        logger_proc.debug(f"📊 Resultados de procesamiento: {len(procesador.preguntas_abiertas)} preguntas abiertas, {len(procesador.preguntas_cerradas)} preguntas cerradas")
        logger_proc.debug(f" ")
    return procesadores

# ----------------------------------------------- PROCESAMIENTO PRINICPAL ---------------------------------------------------------- #
procesadores = procesar_archivos_json(rutas_json) # Llamar a la función principal para procesar todos los archivos JSON


#-------------------------------------------------- CONEXIÓN de python CON BDD ---------------------------------------------------------------#
logger_proc.debug(f"🔍 Cantidad de procesadores generados: {len(procesadores)}")
config = {
    "dbname": "base_de_conocimiento_chatbot",
    "user": "postgres",
    "password": "0909casajardinpaz0707",
    "host": "localhost",
    "port": "5432",
    "docentes":docentes
} 

logger_proc.debug("🗃️ Conectándose a la base de datos...")
bd = GestorBD(config) 
logger_proc.debug("vas a ingresar a la posible carga de datos")

total_reg_resp = 0
total_reg_preguntas =0
total_reg_adj_preg = 0
total_reg_adj_resp= 0

def marcar_preguntas_sin_contexto(preguntas):
    for pregunta in preguntas:
        pregunta.marcar_sin_contexto()
    return preguntas

def agregar_es_administrativa (preguntas):
    for pregunta in preguntas:
        pregunta.marcar_administrativa()
    return preguntas

def marcar_respuestas_cortas(preguntas):
    for pregunta in preguntas:
        for respuesta in pregunta.respuestas:
            respuesta.marcar_como_corta()
    return preguntas

# --------------------------------------- PERSISTENCIA DE DATOS ---------------------------------------------------------------------#
# Persistir preguntas de todos los procesadores
for indice,proc in enumerate(procesadores,start=1): # por cada procesador 
    logger_proc.debug(f"Preguntas cerradas: {len(proc.preguntas_cerradas)} ")
    preguntas_con_contexto = marcar_preguntas_sin_contexto(proc.preguntas_cerradas)
    cont_preg_sin_contexto = 0
    
    for pregunt in preguntas_con_contexto:
        if pregunt.sin_contexto:
            cont_preg_sin_contexto=cont_preg_sin_contexto +1
    
    logger_proc.debug(f"Preguntas sin contexto detectadas: {cont_preg_sin_contexto} ")
    preguntas_con_estado = agregar_es_administrativa (preguntas_con_contexto)
    preguntas_con_respuestas_marcadas = marcar_respuestas_cortas(preguntas_con_estado)
    preguntas_a_procesar = preguntas_con_respuestas_marcadas
    
    total_reg_preguntas=total_reg_preguntas + len(preguntas_a_procesar) # se acumulan cantidad de preguntas cerradas en cada procesamiento de archivo
    logger_proc.debug(f" ")
    logger_proc.debug(f"analizando el json número : {indice}")
    logger_proc.debug(f"Cantidad de Preguntas Cerradas {len(preguntas_a_procesar)}")
    cant_resp= 0
    
    for index,pregunta in enumerate(preguntas_a_procesar,start=1): # se van acumulando la cantidad de respuestas totales
        cant_resp=cant_resp+len(pregunta.respuestas)
    total_reg_resp = total_reg_resp + cant_resp
   
    logger_proc.debug(f"La cantidad total de respuestas en el json {indice} es {cant_resp}")
    bd.persistir_preguntas(preguntas_a_procesar,indice) # persistencia de datos

logger_proc.debug(f"La cantidad total de preguntas : {total_reg_preguntas}")
logger_proc.debug(f"La cantidad total de respuestas: {total_reg_resp}")

bd.cerrar_conexion()
logger_proc.debug("💾 Conexión cerrada y datos guardados.")

