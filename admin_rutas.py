# MANEJO DE RUTAS

#MANEJO DE RUTAS JSON para procesarlos (clasificar mensaje como preguntas y respuestas) y persistirlos 
from clase_ruta import Ruta
# Se pueden definir, se pueden modificar rutas una sola vez y no ir buscando en todo el código. 
ruta_json_1 = Ruta(r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1221091721383903262\chat.json")
ruta_json_2 = Ruta(r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1219817856288686083\chat.json")
ruta_json_3 = Ruta(r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1221091674248446003\chat.json")

rutas_json = [ruta_json_1, ruta_json_2, ruta_json_3]


# MANEJO de RUTAS DE ARCHIVOS ADJUNTOS a los mensajes
from collections import Counter

ruta_images_1 = Ruta(r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1221091721383903262\images")
ruta_images_2= Ruta(r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1219817856288686083\images")
ruta_imagen_3= Ruta(r"C:\Users\lourd\Downloads\Exportación Discord Diseño de Sistemas 2024\export\1221091674248446003\images")

rutas_imagen = [ruta_images_1,ruta_images_2,ruta_imagen_3]

conteo_total = Counter()
conteo_por_carpeta = {}

#  ---- ------ ------ ANALISIS DE ARCHIVOS ADJUNTOS ---- ----- ------#
# NOTA: Se detectaron diferencias entre cantidad de archivos en carpetas (aqui contados en el código que es lo mismo que contarlas a mano)
#  y registros de adjuntos en JSON (es decir, analizar de cada registro del json el campo attachments).
# y también hay diferencias con los registros en la base de datos
# Actualmente los archivos adjuntos no se usan, por lo tanto no se sincronizan ni se limpian.
# Si en el futuro se requiere usar imágenes, PDF, etc., revisar esta parte.

from utilidades_logs import setup_logger
log_adjuntos= setup_logger('log_adj','auditoria_archivos_adjuntos.txt')
#ingresando a cada objeto ruta
for ruta in rutas_imagen:
    extensiones = [
        # Path (uso en clase RUTA) usa suffix para obtener la extensión del archivo.
        archivo.suffix.lower().lstrip('.') # lower: pasa todo a minuscula y lstrip : quita el punto final
        # glob Escanea un directorio (ruta.nombre_ruta) y se obtienen todos los archivos y carpetas dentro de nombre_ruta
        for archivo in ruta.nombre_ruta.glob("*") 
            if archivo.is_file()
    ] # por cada ruta.nombre_ruta (carpetas o directorios supuestamente), se accede a ella para obtener los archivos que posee
      # y por cada archivo en la ruta, se obtiene su extensión se la pasa a minuscula y se le quita el punto 

    #este es el conteo por cada ruta
    conteo = Counter(extensiones) # cuenta la frecuencia de cada elemento único en la lista proporcionada
    #devuelve diccionario con par clave-valor: tipo o extensión - cantidad
    
    # diccionario cuya clave es el nombre de la ruta, y cada ruta toma como valor el conteo
    conteo_por_carpeta[str(ruta)] = conteo

    # Actualiza conteo_total, sumando los valores de conteo a los ya existentes en conteo_total.
    conteo_total.update(conteo)

# Mostrar por carpeta
log_adjuntos.debug("Conteo por carpeta:")
for ruta_str, conteo in conteo_por_carpeta.items(): # método que devuelve pares clave-valor, lo que permite recorrer el diccionario.
    log_adjuntos.debug(f"\n{ruta_str}")
    for ext, cant in conteo.items(): # el conteo es un counter que es un diccionario clave-valor: tipo de archivo o extensión - cantidad
        log_adjuntos.debug(f"  {ext}: {cant}")

# Mostrar total
log_adjuntos.debug("\nConteo total:")
for ext, cant in conteo_total.items(): # es un diccionario clave-valor: tipo o extensión : cantidad
    log_adjuntos.debug(f"{ext}: {cant}")

log_adjuntos.debug(" ")

import pandas as pd
import json
import os

for indice,ruta_json in enumerate(rutas_json,start=1):
    # Cargar el JSON (suponiendo que viene de un archivo)
    data = ruta_json.leer_json()
    # Convertir a DataFrame
    df = pd.DataFrame(data)
    # Expandir la columna de attachments para analizar extensiones
    df_exploded = df.explode("attachments")  # Separa listas en filas individuales

    # Extraer extensiones de archivo
    df_exploded["extension"] = df_exploded["attachments"].apply(lambda x: os.path.splitext(x)[-1] if isinstance(x, str) else None)

    # Contar cuántos archivos hay de cada tipo
    ext_counts = df_exploded["extension"].value_counts()

    log_adjuntos.debug(f"en el json {indice} existen {ext_counts}")