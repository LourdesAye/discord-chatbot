# clasificar un mensaje como pregunta, repregunta o respuesta.
import requests
from database.knowledge_base.llm_analysis.prompts import obtener_prompt_analiza_mensaje
from database.knowledge_base.llm_analysis.config_llama import url,headers,armate_body
import time
from src.utils_for_all.utilidades_logs import setup_logger
from database.knowledge_base.models.clase_preguntas import Pregunta

logger_msj = setup_logger('procesamiento_de_mensajes','logs_procesar_mensajes.txt')
logger_llama = setup_logger('procesamiento_de_mensajes_llama','logs_procesar_mensajes_llama.txt')

MAX_INTENTOS = 3
# Función para llamar a LLaMA vía Groq (adaptala si ya tenés tu propio wrapper)
def llama_clasifica( mensaje, pregunta_abierta):
    body= armate_body(obtener_prompt_analiza_mensaje,pregunta_abierta,mensaje) # establecer url, headers y cuerpo
    # retry automático : si una operación (como un request a una API) falla, el sistema la intenta de nuevo automáticamente.
    # backoff : es el tiempo de espera antes de reintentar. Va aumentando con cada intento fallido, 
    # como una forma de "darle más aire" al servidor para que se recupere.
    # retry automático con backoff
    for i in range(MAX_INTENTOS):
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 429:
            espera = 2 ** i  # 1, 2, 4... segundos
            logger_msj.debug(f"[WARN] Error 429 Too Many Requests. Esperando {espera}s y reintentando (intento {i+1})...")
            logger_llama.debug(f"[WARN] Error 429 Too Many Requests. Esperando {espera}s y reintentando (intento {i+1})...")
            time.sleep(espera)
        else:
            response.raise_for_status()
            respuesta_llama = response.json()["choices"][0]["message"]["content"].strip().upper()
            logger_msj.debug(f" 🧠 IA LLAMA indica que")
            logger_msj.debug(f"          ❓ la pregunta: '{pregunta_abierta.contenido}' y ") 
            logger_msj.debug(f"          ✉️ el mensaje : '{mensaje.contenido}' ")
            logger_msj.debug(f"tienen la relación: {respuesta_llama} ")
            logger_llama.debug(f" 🧠 IA LLAMA indica que")
            logger_llama.debug(f"          ❓ la pregunta: '{pregunta_abierta.contenido}' y ") 
            logger_llama.debug(f"          ✉️ el mensaje : '{mensaje.contenido}' ")
            logger_llama.debug(f"tienen la relación: {respuesta_llama} ")
            return response.json()["choices"][0]["message"]["content"].strip().upper()
    raise Exception("Demasiados intentos fallidos por 429.")


    # response = requests.post(url, headers=headers, json=body) # Hace una petición HTTP POST (procesar datos) a la API con la URL, cabeceras y datos definidos.
    # response.raise_for_status() 
    # es un método de la librería requests en Python que se usa para verificar si la solicitud HTTP fue exitosa. 
    # Si la respuesta del servidor tiene un código de estado que indica un error (cualquier código en el rango 4xx o 5xx), 
    # este método generará una excepción (requests.exceptions.HTTPError).
    # respuesta = response.json()["choices"][0]["message"]["content"].strip().upper()
    # response.json() : convierte la respuesta en formato JSON a un diccionario de Python para poder procesarla.
    # ["choices"] : lista de respuestas del modelo.
    # [0] : primera respuesta.
    # "message": contenido del mensaje.
    # "content" : texto generado.
    # strip().lower() → elimina espacios al inicio/fin y lo pone en minúsculas.
    # return respuesta

# Función principal
def clasificar_mensaje_y_actualizar(mensaje, preguntas_abiertas):
    mejor_relacion = None
    mejor_pregunta = None

    for pregunta in preguntas_abiertas:
        time.sleep(2) # pausa de dos segundos entre request
        inicio = time.time() # momento actual 
        clasificacion = llama_clasifica(mensaje, pregunta)

        if clasificacion in ("RESPUESTA", "REPREGUNTA"):
            mejor_relacion = clasificacion
            mejor_pregunta = pregunta
            break  # una coincidencia es suficiente, no hace falta seguir

        fin = time.time()
        logger_msj.debug(f"[RESULTADO] Clasificación: {clasificacion} (tardó {fin - inicio:.2f} segundos)")

    if mejor_relacion:
        mejor_pregunta.agregar_respuesta(mensaje)
        logger_msj.debug(f"🟢 Mensaje agregado como {mejor_relacion} a: '{mejor_pregunta.contenido}'")
    else:
        # si no hay coincidencias, se trata como nueva pregunta
        nueva_pregunta = Pregunta(mensaje)
        preguntas_abiertas.append(nueva_pregunta)
        logger_msj.debug(f"🟡 NUEVA PREGUNTA ABIERTA: {nueva_pregunta.contenido}")

