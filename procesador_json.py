import pandas as pd
import json
import re
import os
from datetime import datetime, timedelta
from clase_procesador_mensajes import Procesador

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
    # Asegurarse de que 'content' exista y convertir a string (por si hay None)
    df["content"] = df["content"].astype(str).str.strip()

    # Filtrar: se queda solo con los que tienen texto real (no vacío)
    df = df[df["content"] != ""]

    # Filtrar los mensajes irrelevantes visualmente
    visuales_df = df[df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]

    # Filtrar DataFrame sin vacios, quitandole los mensajes visuales irrelevantes (emojis, gifs, etc.)
    df = df[~df["content"].apply(FiltradorContenido.es_contenido_irrelevante_visual)]

    # Filtrar los mensajes que tienen solo combinación de números + signos
    sin_numeros_solos_df = df[df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]

    # Filtrar los mensajes que no tengan solo combinación de números + signos
    df = df[~df["content"].apply(FiltradorContenido.es_solo_numeros_signos)]

    return df, visuales_df, sin_numeros_solos_df


# Función para guardar los CSVs con los resultados
def guardar_csvs(df, visuales_df, sin_numeros_solos_df, nombre_base):
    visuales_df[["content"]].to_csv(f"{nombre_base}_emojis_gifs_descartados.csv", index=False, encoding="utf-8")
    sin_numeros_solos_df[["content"]].to_csv(f"{nombre_base}_numeros_descartados.csv", index=False, encoding="utf-8")
    df[["content"]].to_csv(f"{nombre_base}_json_sin_mensajes_irrelevantes.csv", index=False, encoding="utf-8")


# Función principal para procesar los JSONs
def procesar_archivos_json(rutas_json):
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
        # Esto configura pandas para que no corte columnas ni contenido
        pd.set_option('display.max_columns', None)     # muestra todas las columnas
        pd.set_option('display.max_colwidth', None)     # muestra el contenido completo de cada celda
        pd.set_option('display.width', None)            # ajusta el ancho total automáticamente
        pd.set_option('display.expand_frame_repr', False)  # evita que corte el frame en varias líneas
        print(df.head(5))
        procesador.procesar_dataframe(df,ruta_json)

        
        # Mostrar resultados del procesamiento
        print(f"✅ Procesamiento completado para el archivo {idx}")
        print(f"📂 Archivos guardados para el archivo {idx}: {nombre_base}_emojis_gifs_descartados.csv, {nombre_base}_numeros_descartados.csv, {nombre_base}_json_sin_frases_cortas.csv")
        print(f"📊 Resultados de procesamiento: {len(procesador.preguntas_abiertas)} preguntas abiertas, {len(procesador.preguntas_cerradas)} preguntas cerradas")


# Rutas a los archivos JSON
rutas_json = [
    r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1221091721383903262\chat.json",
    r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1219817856288686083\chat.json",
    r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1221091674248446003\chat.json"
]

# Llamar a la función principal para procesar todos los archivos JSON
procesar_archivos_json(rutas_json)

# Ahora se tiene:
# procesador.preguntas_abiertas
# procesador.preguntas_cerradas
# procesador.mensajes_sueltos
# procesador.respuestas_sueltas

