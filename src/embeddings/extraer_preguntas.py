from utils_for_all.conexion_bdd import config
from utils_for_all.utilidades_logs import setup_logger,guardar_pregunta
import psycopg2 
from psycopg2.extras import DictCursor

def obtener_preguntas_y_metadatos():
    logger_preguntas = setup_logger("logger_embeddings", "logs_preguntas_para_embeddings.txt")
    preguntas, metadatos = [], []

    try:
        conn = psycopg2.connect(**config) # es la conexión a tu base de datos PostgreSQL.
        # DictCursor hace que los resultados sean accesibles por nombre de columna (ej. fila["texto"]).
        cursor = conn.cursor(cursor_factory=DictCursor) # permite ejecutar consultas SQL y recorrer los resultados.
        cursor.execute("""
            SELECT DISTINCT p.id_pregunta, p.texto
            FROM preguntas p
            JOIN respuestas r ON r.pregunta_id = p.id_pregunta
            WHERE r.es_validada = true
              AND (p.sin_contexto IS NULL OR p.sin_contexto = false)
              AND (p.es_administrativa IS NULL OR p.es_administrativa = false)
        """) 
        resultados = cursor.fetchall() # Obtiene todos los resultados de la consulta

        # Extrae las preguntas y genera metadatos para vincular luego con los embeddings.
        preguntas = [fila["texto"] for fila in resultados]
        metadatos = [{"id": fila["id_pregunta"]} for fila in resultados]

        for i, pregunta in enumerate(preguntas, start=1):
            guardar_pregunta(pregunta, i, "logs_preguntas_para_embeddings.txt")

    except Exception as e:
        logger_preguntas.error(f"Error: {e}")

    finally: # asegura que se cierren la conexión y el cursor aunque ocurra un error.
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    return preguntas, metadatos

    # cursor = conn.cursor(cursor_factory=DictCursor)
    # para devolver objeto de tipo DictRow, que se comporta como un diccionario, pero también como una tupla. Es decir:
        # Podés acceder por clave: fila["texto"]
        # Pero también por índice: fila[1]
    # Y cuando lo imprimís como una lista: print(list(fila)) → te devuelve algo como [228, 'entonces, ¿cómo...']
        # print(type(resultados[0]))
        # print(resultados[0]) #  Se ven como listas porque DictRow se imprime así, pero siguen siendo accesibles por claves.
    # print(resultados)
        # print(type(resultados[0])) # <class 'psycopg2.extras.DictRow'>
    # print(resultados[0]) #  Se ven como listas porque DictRow se imprime así, pero siguen siendo accesibles por claves.
    # print(resultados)