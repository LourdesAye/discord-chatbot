import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from utils_for_all.config_rutas import LOG_DIR_ABS
import pandas as pd

# Ruta base donde estarán todas las carpetas de logs con timestamp
directorio_logs = LOG_DIR_ABS

# Generar nombre de carpeta con fecha y hora
FECHA_LOG = datetime.now().strftime("logs_%d_%m_%y_%H_%M")
LOG_DIR_FINAL = os.path.join(directorio_logs, FECHA_LOG)

FECHA_CSV = datetime.now().strftime("csv_%d_%m_%y_%H_%M")
CSV_DIR_FINAL = os.path.join(directorio_logs, FECHA_CSV)

def setup_logger(name, log_file):
    nombre_carpeta = f"{LOG_DIR_FINAL}"
    # Crear carpeta si no existe
    os.makedirs(nombre_carpeta, exist_ok=True)
    ruta_log = os.path.join(nombre_carpeta, log_file)

    logger = logging.getLogger(name)  # Cada proceso tiene su propio logger
    if not logger.handlers:  # Para evitar handlers duplicados
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(ruta_log, mode='a', encoding='utf-8') # 'a' = append
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.propagate = False # evitar que se muestre por consola  
    return logger

#Ejemplo de uso 
# 1 - creación y configuración de logger 
# logger_proceso_grande = setup_logger('proceso_grande', 'log_proceso_grande.txt')
# logger_pequeno_1 = setup_logger('proceso_pequeno_1', 'log_proceso_pequeno_1.txt')
# logger_pequeno_2 = setup_logger('proceso_pequeno_2', 'log_proceso_pequeno_2.txt')

# 2- llamado en funciones o procesamiento 
# logger_proceso_grande.info('Inicio del proceso grande')
# logger_proceso_grande.debug('Inicio del proceso grande')
# logger_pequeno_1.info('Proceso pequeño 1 en ejecución')
# logger_pequeno_1.debug('Proceso pequeño 1 en ejecución')

def guardar_pregunta_y_respuestas_en_log(pregunta, numero_pregunta, ruta_archivo):
    nombre_carpeta = f"{LOG_DIR_FINAL}"
    os.makedirs(nombre_carpeta, exist_ok=True)
    ruta_completa = os.path.join(nombre_carpeta, ruta_archivo)

    with open(ruta_completa, "a", encoding="utf-8") as f:
        f.write("═══════════════════════════════════════════════════════\n")
        f.write(f"[PREGUNTA {numero_pregunta}]\n")
        f.write(pregunta.contenido + "\n")
        f.write(pregunta.timestamp + "\n")
        f.write("\n[RESPUESTAS]\n")
        if pregunta.respuestas:
            for idx, respuesta in enumerate(pregunta.respuestas, start=1):
                f.write(f"  → Fecha de Respuesta {idx}: {respuesta.timestamp}\n")
                f.write(f"      → Autor Respuesta {idx}: {respuesta.autor}\n")
                f.write(f"          → Respuesta {idx}: {respuesta.contenido}\n")
        else:
            f.write("⚠️ No hubo respuestas para esta pregunta.\n")
        f.write("═══════════════════════════════════════════════════════\n\n")

def guardar_respuestas_sin_pregunta(respuestas_huerfanas, ruta_archivo="log_respuestas_sin_pregunta.txt"):
    nombre_carpeta = f"{LOG_DIR_FINAL}"
    os.makedirs(nombre_carpeta, exist_ok=True)
    ruta_completa = os.path.join(nombre_carpeta, ruta_archivo)
    with open(ruta_completa, "w", encoding="utf-8") as f:
        f.write("═══════════════════════════════════════════════════════\n")
        f.write("LOG DE RESPUESTAS SIN PREGUNTA\n")
        f.write("═══════════════════════════════════════════════════════\n\n")
        
        if not respuestas_huerfanas:
            f.write("✅ No quedaron respuestas sin pregunta.\n")
        else:
            for idx, respuesta in enumerate(respuestas_huerfanas, start=1):
                f.write(f"[RESPUESTA {idx}]\n")
                f.write(f"Fecha: {respuesta.timestamp}\n")
                f.write(f"Autor: {respuesta.autor}\n")
                f.write(f"Contenido: {respuesta.contenido}\n")
                f.write("-------------------------------------------------------\n\n")

# Guarda un DataFrame filtrado principal y los resultados de cada filtro en CSVs separados.
# Si algún DataFrame está vacío, se genera un CSV con un mensaje aclaratorio.
def guardar_resultados_en_csvs(df_filtrado, filtros_aplicados,nombre_base):

    nombre_carpeta = f"{CSV_DIR_FINAL}"
    if not os.path.exists(nombre_carpeta):
        os.makedirs(nombre_carpeta) # para crear una carpeta con el nombre base si no existe.
    
    nombre_archivo_filtrado = f"{nombre_base}_filtrado_limpio.csv"
    ruta_salida_filtrado = os.path.join(nombre_carpeta, nombre_archivo_filtrado)
    df_filtrado.to_csv(ruta_salida_filtrado, index=False,encoding="utf-8")
    
    for nombre_filtro, df_filtrado in filtros_aplicados.items():
        nombre_archivo = f"{nombre_base}_{nombre_filtro}.csv"
        ruta_salida = os.path.join(nombre_carpeta, nombre_archivo)
        if df_filtrado.empty:
            # se crea un DataFrame con un mensaje para informar que no hay coincidencias
            mensaje = pd.DataFrame({"info": [f"No se encontraron mensajes que cumplan con el filtro: {nombre_filtro}"]})
            mensaje.to_csv(ruta_salida, index=False,encoding="utf-8")
        else:
            df_filtrado.to_csv(ruta_salida, index=False,encoding="utf-8")
    # os.path.join(nombre_carpeta, archivo.csv) para armar la ruta completa al archivo dentro de esa carpeta.

def guardar_pregunta(pregunta, numero_pregunta, ruta_archivo):
    nombre_carpeta = f"{LOG_DIR_FINAL}"
    os.makedirs(nombre_carpeta, exist_ok=True)
    ruta_completa = os.path.join(nombre_carpeta, ruta_archivo)

    with open(ruta_completa, "a", encoding="utf-8") as f:
        f.write("═══════════════════════════════════════════════════════\n")
        f.write(f"[PREGUNTA {numero_pregunta}]\n")
        f.write(pregunta+ "\n")
        f.write("═══════════════════════════════════════════════════════\n\n")

