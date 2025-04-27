import json
import pandas as pd
import re
import os
from datetime import datetime, timedelta

# usuarios docentes que solo responden no preguntan
usuarios_docentes = ["ezequieloescobar", "aylenmsandoval", "lucassaclier"]

# Frases comunes para detectar preguntas explícitas o implícitas
frases_clave_preguntas = [
    "cómo", "cuándo", "qué", "cuál", "dónde", "por qué", "para qué",
    "qué pasa si", "tengo una consulta", "tengo una duda", "tengo una pregunta",
    "mi duda es", "mi consulta es", "quisiera consultar", 
    "quería saber si", "me surgió la duda", "necesito saber si", "me pregunto si",
    "alguien sabe", "una duda", "una consulta","necesito ayuda", "es posible"
]
# frases habituales en respuestas de docentes validando respuesta de alumno
frases_validacion_docente ={"perfecto", "exacto","buenísimo"}

#frases de alumnos para cerrar el ida y vuelta de pregunta y respuestas
frases_cierre_alumnos = {"gracias","perfecto","buenísimo","genial","muchas","joya"}

def es_docente(autor: str) -> bool:
    return autor.lower() in usuarios_docentes

# si un mensaje completo es una pregunta.
# La función toma una fila completa del DataFrame para analizar si el mensaje es pregunta 
# a partir del autor y de ciertos patrones
def es_pregunta(mensaje: str) -> bool:
    texto = mensaje. lower().strip() # convierte el mensaje que esta en texto para pasarlo a minúscula y le quita los espacios que pueda tener al incio y al final

    # Si contiene signos de interrogación
    if "?" in texto or "¿" in texto:
        return True

    # Si contiene alguna frase típica
    for frase in frases_clave_preguntas:
        if frase in texto:
            return True

    return False

def es_respuesta_docente(autor: str)-> bool:
    autor = autor.lower().strip() #lleva el autor a minuscula y le quita los espacios al inicio y al final
    return autor in usuarios_docentes # verificacion directa con in sin usar for

def es_mensaje_de_cierre_alumno(mensaje: str) -> bool:
    texto = mensaje.lower().strip()
    for frase in frases_cierre_alumnos:
        if frase in texto and len(texto) <= 10:  # Evitar mensajes largos tipo "gracias + nueva pregunta"
            return True
    return False

# para detectar si dentro del mensaje hay indicios de una nueva pregunta.
def contiene_pregunta(mensaje: str) -> bool:
    mensaje = mensaje.lower().strip()
    
    # Detectar si hay signos de pregunta
    if "?" in mensaje or "¿" in mensaje:
        return True

    # Detectar si contiene alguna frase típica de pregunta
    for frase in frases_clave_preguntas:
        if frase in mensaje:
            return True

    return False

def es_mensaje_de_validacion_docente(mensaje: str) -> bool:
    mensaje = mensaje.lower().strip()
    for frase in frases_validacion_docente:
        if frase in mensaje:
            return True
    return False

