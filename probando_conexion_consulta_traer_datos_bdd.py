# --- IMPORTANDO LIBRERÍAS NECESARIAS --- # 
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# --- CARGA DE VARIABLES DE ENTORNO A TRAVÉS DE .ENV A UN DICCIONARIO DE CONFIGURACIO --- #
# Cargar variables desde .env
load_dotenv()

# Obtener configuración desde variables de entorno (.env) y generar diccionario con los parámetros de conexión
config = {
    "dbname": os.getenv("DB_NAME"), # nombre de la base de datos
    "user": os.getenv("DB_USER"), # usuario de la base de datos
    "password": os.getenv("DB_PASSWORD"), # contraseña del usuario de la base de datos
    "host": os.getenv("DB_HOST"), # dirección del servidor de la base de datos
    "port": os.getenv("DB_PORT") # puerto de conexión a la base de datos
}

# la notación **config es solo para definición de funciones no para otra cosa
    # **argumento: se le indica a python que se le pasa un diccionario


# --- CONEXIÓN A LA BASE DE DATOS, CONSULTA DE DATOS Y TRAERLOS POR PANTALLA --- #

try: # para manejo de errores

    # --- CONEXIÓN A LA BASE DE DATOS --- #
    # conn : es la conexión a la base de datos
    conn = psycopg2.connect(**config) # se establece conexión con la base de datos
    # Se crea un cursor (objeto que permite ejecutar consultas SQL) 
        # utiliza RealDictCursor (para que resultados se devuelvan como diccionarios, no como tuplas)
            # {'id_autor': 1, 'nombre_autor': 'ezequieloescobar', 'es_docente': True}

    # with obtenerConFuncionesRecurso as renombroObtencionRecurso:
        # crea un bloque de contexto
        # es decir, que a partir de la indentación ( espacios en blanco al principio de una línea de código para definir bloques de código,)
        # se usa el recurso definido como renombroObtencionRecurso y también se cierra

    # Funcionamiento de with internamente: 
        # 1 - abre o inicializa el recurso (obtenerConFuncionesRecurso.__enter__()), 
        # 2 - asigna obtenerConFuncionesRecurso a renombroObtencionRecurso
        # 3 - ejecuta el bloque indentado usando renombroObtencionRecurso
        # 4 - cierra o libera el recurso (renombroObtencionRecurso.__exit__())
        # No se necesita un open o un close

    # cursor(): Creación del cursor para ejecutar consultas SQL y recuperar resultados
    # cursor_factory=RealDictCursor :  tipo especial de cursor
        # hace que los resultados se devuelvan como lista de diccionarios, y no como lista de tuplas
            # Sin RealDictCursor: [(1, 'Lourdes', True)]
            # Con RealDictCursor: [{'id_autor': 1, 'nombre_autor': 'Lourdes', 'es_docente': True}]
                # acceder a los datos por nombre de columna fila['nombre_autor']
    with conn.cursor(cursor_factory=RealDictCursor) as cur: # as cur: le da un nombre al cursor dentro del bloque with.

        # --- CONSULTA SQL PARA TRAER DATOS DE LA BASE DE DATOS --- #
        query = "SELECT id_autor, nombre_autor, es_docente FROM autores where id_autor between %s and %s;"
        cur.execute(query,(1,5,)) # ejecutar la consulta SQL con parámetros (1 y 5 reemplazan los %s en la consulta)
        
        resultados = cur.fetchall() # para obtener todos los resultados : retorna una lista
            # en este caso, cada elementos de la lista es un diccionario (por RealDictCursor)

        # --- IMPRIMIR LOS RESULTADOS POR PANTALLA --- #
        for index,fila in enumerate(resultados,start=1): 
            print(f"Se van a obtener los resultados de la fila {index} : {fila}")
            print(f"ID: {fila['id_autor']}, Nombre: {fila['nombre_autor']}, Es Docente: {fila['es_docente']} \n")
            
except psycopg2.Error as e:
    print(f"Error al conectar o consultar la base de datos: {e}")

finally:
    if conn:
        conn.close()


# cur.execute(query,parametros)
    # execute() : para enviar consulta SQL a la base de datos 
        # ejecutar comandos como : SELECT, INSERT, UPDATE, DELETE, etc
    # query
        # el comando o consulta SQL 
            # utilizar placeholders (espacios reservados)
                # se escribe como %s, sin importar el tipo de dato (texto, número, booleano, etc.) 
                # se utiliza para evitar inyecciones SQL, hacer el código más limpio y mantenible 
                # (concatenar strings manualmente puede ser peligroso y propenso a errores)
    # parametros
        # va solo si corresponde, es el segundo argumento, es una tupla con los valores a insertar en lugar de los placeholders.
   
# Ejemplo: 
# query = "SELECT * FROM autores WHERE nombre_autor = %s AND es_docente = %s;"
# valores = ("Lourdes", True)
# cur.execute(query, valores)

# query = "SELECT * FROM autores WHERE id_autor = %s;"
# cur.execute(query, (1,))
    # (1,) es una tupla con el valor que va a reemplazar ese %s.
        # # (1) Es solo un numero, no una tupla
