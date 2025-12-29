import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.config_rutas import LOG_DIR_ABS
import pandas as pd

# === Configuración inicial ===
FECHA_LOG = datetime.now().strftime("logs_%d_%m_%y_%H_%M")
FECHA_CSV = datetime.now().strftime("csv_%d_%m_%y_%H_%M")

LOG_DIR_FINAL = os.path.join(LOG_DIR_ABS, FECHA_LOG)
CSV_DIR_FINAL = os.path.join(LOG_DIR_ABS, FECHA_CSV)

def preparar_ruta(base_dir, nombre_archivo):
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, nombre_archivo)

def setup_logger(nombre_logger, nombre_archivo):
    ruta_log = preparar_ruta(LOG_DIR_FINAL,nombre_archivo)
    logger = logging.getLogger(nombre_logger)  # Cada proceso tiene su propio logger
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

def guardar_pregunta_y_respuestas_en_log(pregunta, numero_pregunta, nombre_archivo):
    ruta = preparar_ruta(LOG_DIR_FINAL,nombre_archivo)
    with open(ruta, "a", encoding="utf-8") as f:
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

# Guarda un DataFrame filtrado principal y los resultados de cada filtro en CSVs separados.
# Si algún DataFrame está vacío, se genera un CSV con un mensaje aclaratorio.
def guardar_resultados_en_csvs(df_filtrado, filtros_aplicados,nombre_base):
    
    nombre_archivo_filtrado = f"{nombre_base}_filtrado_limpio.csv"
    ruta_salida_filtrado = preparar_ruta(CSV_DIR_FINAL,nombre_archivo_filtrado)    
    
    df_filtrado.to_csv(ruta_salida_filtrado, index=False,encoding="utf-8")
    
    for nombre_filtro, df_filtrado in filtros_aplicados.items():
        nombre_archivo = f"{nombre_base}_{nombre_filtro}.csv"
        ruta_final = preparar_ruta(CSV_DIR_FINAL,nombre_archivo)
        if df_filtrado.empty:
            # se crea un DataFrame con un mensaje para informar que no hay coincidencias
            mensaje = pd.DataFrame({"info": [f"No se encontraron mensajes que cumplan con el filtro: {nombre_filtro}"]})
            mensaje.to_csv(ruta_final, index=False,encoding="utf-8")
        else:
            # Creamos una fila resumen con la cantidad
            # se va a crear un nuevo DataFrame llamado fila_conteo
            fila_conteo = pd.DataFrame({
                col: [""] for col in df_filtrado.columns # toma las mismas columnas que df_filtrado con una única fila que rellena con una cadena vacia
            })
            fila_conteo.iloc[0, 0] = f"Cantidad de registros: {len(df_filtrado)}" # iloc[fila, columna] , iloc[0, 0] = primera fila, primera columna
            # Concatenar el DataFrame filtrado con la fila resumen
            df_con_fila_extra = pd.concat([df_filtrado, fila_conteo], ignore_index=True)
            df_con_fila_extra.to_csv(ruta_final, index=False, encoding="utf-8")
    # os.path.join(nombre_carpeta, archivo.csv) para armar la ruta completa al archivo dentro de esa carpeta.

def guardar_pregunta(pregunta, numero_pregunta, ruta_archivo):
    ruta = preparar_ruta(LOG_DIR_FINAL,ruta_archivo)
    with open(ruta, "a", encoding="utf-8") as f:
        f.write("═══════════════════════════════════════════════════════\n")
        f.write(f"[PREGUNTA {numero_pregunta}]\n")
        f.write(pregunta+ "\n")
        f.write("═══════════════════════════════════════════════════════\n\n")

