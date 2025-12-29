"""
MAIN OFFLINE — Pipeline inicial para construir la base de conocimiento.

Este archivo se ejecuta solamente cuando quiero generar o actualizar desde cero
la información base del chatbot a partir de los archivos JSON exportados de Discord.

¿Qué hace este proceso?
1. Busca los archivos JSON.
2. Filtra mensajes irrelevantes (vacíos, stickers, GIFs, etc.).
3. Identifica preguntas, respuestas y sus asociaciones.
4. Cierra preguntas y aplica análisis adicional.
5. Persiste toda la información procesada en la base de datos relacional.
6. Genera los embeddings y crea/actualiza la base vectorial.

¿Por qué existe este main por separado?
- Porque este procesamiento es "pesado" y ocurre una sola vez o cada cierto tiempo.
- No necesita conexión a Discord.
- No debe ejecutarse cada vez que inicio el bot.
- Deja lista la base de conocimiento para el funcionamiento del chatbot.

Este main termina y se cierra; no queda corriendo en segundo plano.
"""
from utils.conexion_bdd import config
from database.analizador_preguntas_cerradas import AnalizadorPreguntasCerradas
from database.clase_cargar_bdd import GestorBD
from processing.procesamiento_json import procesar_archivos_json
from utils.utilidades_logs import setup_logger
from utils.config_rutas import BuscadorArchivos
from embeddings.gestor_vectores import GestorBaseVectorial
from langchain_huggingface import HuggingFaceEmbeddings

def main(): 
    # LOGGER para seguimiento de la carga de datos
    logger_proc= setup_logger('carga_procesador','log_procesamiento_con_preguntas_cerradas.txt')

    # PROCESAMIENTO de los JSONs
    buscador_archivos = BuscadorArchivos()
    rutas_json = buscador_archivos.obtener_rutas_json() #  ⚠️🚨❗REFACTOR  ⚠️🚨❗, ver qué pasa si no hay jsons (si funciona)

    logger_proc.debug(f" 🗂️ Cantidad de archivos JSON encontrados: {len(rutas_json)}")
    if len(rutas_json) == 0:
        logger_proc.debug(" ❌ No se encontraron archivos JSON para procesar. Finalizando ejecución.")
        exit(1)  # Salir del programa si no hay archivos JSON   
    
    procesadores = procesar_archivos_json(rutas_json) # función para procesar todos los archivos JSON
    logger_proc.debug(f" 🔍 Cantidad de procesadores generados: {len(procesadores)}")
    logger_proc.debug(" 🗃️ Conectándose a la base de datos...") 

    # PERSISTENCIA EN BASE DE DATOS
    # configuración y conexión con BDD
    bd = GestorBD(config) 

    # contador de respuestas de todos los json
    cant_total_resp = 0 
    # contador de preguntas de todos los json
    cant_total_preg =0 

    # Análisis y persistencia de preguntas cerradas por cada procesador
    for indice,proc in enumerate(procesadores,start=1): # por cada procesador 
        analizador = AnalizadorPreguntasCerradas(proc.preguntas_cerradas)
        #se aplica analisis de preguntas sin contexto, preguntas administrativas y respuestas validadas
        cantidad_preguntas_json, cantidad_respuestas_json, preguntas_a_procesar = analizador.aplicar_analisis_preguntas(indice)
        # contador de preguntas y respuestas que va acumulando por cada json
        cant_total_preg = cant_total_preg + cantidad_preguntas_json
        cant_total_resp = cant_total_resp + cantidad_respuestas_json
        # persistencia de datos de la lista de preguntas cerradas con el analisis aplicado
        bd.persistir_preguntas(preguntas_a_procesar,indice)

    # Resumen final de la carga de datos
    logger_proc.debug(f" ")
    logger_proc.debug(f" ✅ La cantidad total de preguntas generadas : {cant_total_preg}")
    logger_proc.debug(f" ✅ La cantidad total de respuestas generadas : {cant_total_resp}")
    bd.cerrar_conexion() # cerrar conexión con bdd
    logger_proc.debug(f" ")
    logger_proc.debug(" 💾 Conexión cerrada y datos guardados.")


    # PROBABLEMENTE ESTO SE QUITE CUANDO EL CHATBOT ESTÉ FUNCIONANDO CORRECTAMENTE
    # GESTIÓN DE LA BASE VECTORIAL DE EMBEDDINGS
    # configuración del modelo de embeddings y gestor de base vectorial
    modelo = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") # modelo liviano y rápido
    gestor_base_vectorial = GestorBaseVectorial(modelo) # gestor de base vectorial para realizar operaciones: crear, buscar y eliminar

    # crear base de datos de vectores una vez persistidos los datos
    vectordb = gestor_base_vectorial.crear_si_no_existe()

    # Opción 2: Forzar actualización si hay cambios en BDD
    #if gestor.existe_base() and gestor.verificar_consistencia():
    #    gestor.crear_si_no_existe(forzar_actualizacion=True)

    # probar búsqueda semántica en embeddings
    if vectordb:
        gestor_base_vectorial.buscar("¿Qué es Github?")
        gestor_base_vectorial.buscar("¿Cómo se usa el patrón state?")
        gestor_base_vectorial.buscar("¿qué es java?")

if __name__ == "__main__":
    main()


# Ejecutarlo por consola con
# python main_offline.py
# para construir o actualizar la base de conocimiento.

