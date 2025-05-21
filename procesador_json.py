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
from main.procesamiento_json import procesar_archivos_json
from main.conexion_bdd import config
from main.analizador_preguntas_cerradas import AnalizadorPreguntasCerradas
# ------------------------------------------------- LOGGER -------------------------------------------------------------#
# agregando logger para seguimiento de la carga de datos
logger_proc= setup_logger('carga_procesador','log_carga_de_procesador_con_preguntas_cerradas.txt')

#-------------------------------------------Función de PROCESAMIENTO-------------------------------------------------------#
#  Función principal para procesar los JSONs
procesadores = procesar_archivos_json(rutas_json) # Llamar a la función principal para procesar todos los archivos JSON

#-------------------------------------------------- CONEXIÓN de python CON BDD ---------------------------------------------------------------#
logger_proc.debug(f"🔍 Cantidad de procesadores generados: {len(procesadores)}")

logger_proc.debug("🗃️ Conectándose a la base de datos...")
bd = GestorBD(config) 
logger_proc.debug("vas a ingresar a la posible carga de datos")

total_reg_resp = 0
total_reg_preguntas =0

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
    analizador = AnalizadorPreguntasCerradas(proc.preguntas_cerradas)
    cantidad_preguntas_json, cantidad_respuestas_del_json, preguntas_a_procesar = analizador.aplicar_analisis_preguntas()
    total_reg_preguntas = total_reg_preguntas + cantidad_preguntas_json
    total_reg_resp = total_reg_resp + cantidad_respuestas_del_json

    logger_proc.debug(f"La cantidad total de respuestas en el json {indice} es {cantidad_respuestas_del_json}")
    bd.persistir_preguntas(preguntas_a_procesar,indice) # persistencia de datos

logger_proc.debug(f"La cantidad total de preguntas : {total_reg_preguntas}")
logger_proc.debug(f"La cantidad total de respuestas: {total_reg_resp}")

bd.cerrar_conexion()
logger_proc.debug("💾 Conexión cerrada y datos guardados.")

