# CONFIGURACIÓN INICIAL
from psycopg import connect
# permite que los resultados de las consultas sean devueltos como diccionarios en lugar de tuplas
# permite acceder a los valores de las columnas usando sus nombres, en lugar de depender de índices numéricos.
from psycopg.rows import dict_row
from clase_preguntas import Pregunta
from clase_respuestas import Respuesta

# lista de docentes
docentes = ["ezequieloescobar", "aylenmsandoval", "lucassaclier", "facuherrera_8", "ryan129623"]

def es_docente(nombre_usuario):
    return nombre_usuario in docentes
    

# conexión con la base de datos
conn = connect(
    dbname="base_de_conocimiento_chatbot",
    user="postgres",
    password="0909casajardinpaz0707",
    host="localhost",
    port="5432",
    row_factory=dict_row # para que pueda usar nombres de columnas en lugar de índices
)

# función para buscar o insertar autor
def insertar_o_obtener_autor(conn,nombre_autor): # recibe conexión con la bdd, el autor
    with conn.cursor() as cur: # crea un cursor, que actúa como un "puntero" para ejecutar consultas y recorrer los resultados.
        cur.execute("SELECT id_autor FROM autores WHERE nombre_autor = %s", (nombre_autor,)) #consulta por el nombre del autor en la tabla autor
        fila = cur.fetchone() # Obtiene la primera fila del resultado (si existe).
        if fila: # Si fila no es None, el autor existe
            return fila["id_autor"] # devuelve el id_autor.
        cur.execute(
            "INSERT INTO autores (nombre_autor, es_docente) VALUES (%s, %s) RETURNING id_autor", # Inserta un nuevo autor en la tabla
            (nombre_autor,es_docente(nombre_autor)) # RETURNING id hace que la consulta devuelva el id del nuevo autor insertado.
        )
        return cur.fetchone()["id_autor"] # Obtiene la fila resultante de la consulta INSERT y extrae el id_autor recién generado.


# función para insertar un mensaje que puede ser una pregunta o una respuesta (por este motivo se setean atributos)
def insertar_mensaje(conn, id_mensaje_discord, autor_id, fecha_mensaje, 
                     contenido, es_pregunta=False, es_respuesta=False, origen=None):
    with conn.cursor() as cur: # crea un cursor, que actúa como un "puntero" para ejecutar consultas y recorrer los resultados.
        cur.execute(
            """
            INSERT INTO mensajes (
                id_mensaje_discord,
                autor_id,
                fecha_mensaje,
                contenido,
                es_pregunta,
                es_respuesta,
                origen
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_mensaje;
        """, (
            id_mensaje_discord,
            autor_id,
            fecha_mensaje,
            contenido,
            es_pregunta,
            es_respuesta,
            origen
        )
        ) # inserta un mensaje en la tabla mensajes
        id_mensaje = cur.fetchone()[id_mensaje] #  RETURNING id_mensaje permite que se obtenga el id de ese mensaje que sirve para la pregunta o respuesta
        conn.commit() # CUIDADO! el commit va aquí? Commit al final de cada carga o lote, no por cada inserción.
        return id_mensaje

# Función para insertar una pregunta
def insertar_pregunta (conn, pregunta: Pregunta , id_mensaje):
    with conn.cursor() as cur: # crea un cursor, que actúa como un "puntero" para ejecutar consultas y recorrer los resultados.
        cur.execute(
            """
            INSERT INTO preguntas (mensaje_id,texto,esta_cerrada)
            VALUES (%s, %s, %s) RETURNING id_pregunta
            """,
            (id_mensaje,pregunta.contenido,True)
        )
        return cur.fetchone()["id_pregunta"]

'''
CREATE TABLE respuestas (
    id_respuesta SERIAL PRIMARY KEY,
    mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
    pregunta_id INTEGER NOT NULL REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
    texto TEXT NOT NULL,
    orden INTEGER,
    es_validada BOOLEAN DEFAULT FALSE
);

'''

# PENDIENTE
# PENDIENTE ----------------------------------------------------------------------
# Función para insertar una respuesta
def insertar_respuesta(conn, respuesta: Respuesta, mensaje_id, pregunta_id, orden):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO respuestas (mensaje_id, pregunta_id,texto, orden, es_validada)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (mensaje_id, pregunta_id, respuesta.contenido,orden,respuesta.es_validada)
            # aca debemos analizar cómo obtener orden que sale desde que se procesa un mensaje como una respuesta : ver donde se inicializa, donde suma .
            # aca debemos analizar cuando esta validada la respuesta desde que se procesa un mensaje como respuesta de docente o docente cierra conversacion validando respuesta del alumno 
        )
        return cur.fetchone()["id"]
    

# Función para insertar archivos adjuntos (si hay)
def insertar_attachment(conn, mensaje_id, url, tipo):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO attachments (mensaje_id, url, tipo)
            VALUES (%s, %s, %s) RETURNING id
            """,
            (mensaje_id, url, tipo)
        )
        return cur.fetchone()["id"]


'''
Todas las funciones devuelven el ID generado por la base, que luego podés usar para asociar elementos.
La integridad referencial se respeta porque siempre primero insertás el autor, luego la pregunta, 
y luego las respuestas ligadas a esa pregunta.

Si alguna tabla tiene ON DELETE CASCADE u otras reglas, te conviene definirlas bien en PostgreSQL.
Podés encapsular esto en una clase RepositorioDB o similar, si querés hacerlo más orientado a objetos.

'''

#Función para insertar autores
# Siempre devuelve el id del autor, tanto si ya existe como si lo crea en ese momento. 
# Esto permite asegurar la clave foránea en mensaje
def insertar_autor(cursor, nick):
    cursor.execute("SELECT id FROM autores WHERE nick_discord = %s", (nick,))
    autor = cursor.fetchone()
    if autor:
        return autor[0]
    else:
        cursor.execute(
            "INSERT INTO autores (nick_discord, rol) VALUES (%s, %s) RETURNING id",
            (nick, 'desconocido')
        )
        return cursor.fetchone()[0]

''' ver diferencias 
def insertar_autor(cursor, autor):
    cursor.execute("""
        INSERT INTO autores (id_discord, nombre)
        VALUES (%s, %s)
        ON CONFLICT (id_discord) DO UPDATE SET nombre = EXCLUDED.nombre
        RETURNING id
    """, (autor.id_discord, autor.nombre))
    return cursor.fetchone()[0]
'''

# Función para insertar pregunta, respuestas y adjuntos
def guardar_pregunta_en_db(pregunta, conn):
    cursor = conn.cursor()

    # Insertar autor de la pregunta
    autor_id = insertar_autor(cursor, pregunta.autor)

    # Insertar la pregunta
    cursor.execute(
        """
        INSERT INTO preguntas (id, autor_id, contenido, timestamp, cerrada)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (pregunta.id_pregunta, autor_id, pregunta.contenido, pregunta.timestamp, True)
    )

    # Insertar adjuntos de la pregunta
    for adj in pregunta.attachments:
        cursor.execute(
            """
            INSERT INTO adjuntos (mensaje_id, url, tipo)
            VALUES (%s, %s, %s)
            """,
            (pregunta.id_pregunta, adj['url'], adj.get('tipo', 'desconocido'))
        )

    # Insertar respuestas
    for respuesta in pregunta.respuestas:
        autor_resp_id = insertar_autor(cursor, respuesta.autor)

        cursor.execute(
            """
            INSERT INTO respuestas (id, pregunta_id, autor_id, contenido, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (respuesta.id_respuesta, pregunta.id_pregunta, autor_resp_id, respuesta.contenido, respuesta.timestamp)
        )

        for adj in respuesta.attachments:
            cursor.execute(
                """
                INSERT INTO adjuntos (mensaje_id, url, tipo)
                VALUES (%s, %s, %s)
                """,
                (respuesta.id_respuesta, adj['url'], adj.get('tipo', 'desconocido'))
            )

    conn.commit()
    cursor.close()


# Ejemplo de insertar_pregunta
def insertar_pregunta(cursor, pregunta: Pregunta) -> int:
    autor_id = insertar_autor(cursor, pregunta.autor)
    cursor.execute(
        """
        INSERT INTO preguntas (id_discord, autor_id, contenido, timestamp, cerrada)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (pregunta.id_pregunta, autor_id, pregunta.contenido, pregunta.timestamp, pregunta.cerrada)
    )
    return cursor.fetchone()[0]  # Este es el ID real generado por la base

# Ejemplo de insertar_respuesta
def insertar_respuesta(cursor, respuesta: Respuesta, pregunta_id: int) -> int:
    autor_id = insertar_autor(cursor, respuesta.autor)
    cursor.execute(
        """
        INSERT INTO respuestas (id_discord, pregunta_id, autor_id, contenido, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (respuesta.id_respuesta, pregunta_id, autor_id, respuesta.contenido, respuesta.timestamp)
    )
    return cursor.fetchone()[0]

# cómo guardar ids
id_pregunta = insertar_pregunta(cursor, pregunta)
for respuesta in pregunta.respuestas:
    id_respuesta = insertar_respuesta(cursor, respuesta, id_pregunta)
    for adjunto in respuesta.attachments:
        insertar_adjunto(cursor, adjunto, id_respuesta)

# lo mismo que antes pero con diccionario
ids_preguntas = {}
for pregunta in procesador.preguntas_cerradas:
    id_pregunta = insertar_pregunta(cursor, pregunta)
    ids_preguntas[pregunta.id_pregunta] = id_pregunta

# para datos adjuntos 
def insertar_adjunto(cursor, url, mensaje_id):
    cursor.execute("""
        INSERT INTO adjuntos (mensaje_id, url)
        VALUES (%s, %s)
    """, (mensaje_id, url))


# script principal 
import psycopg2

# Conexión
conn = psycopg2.connect(
    dbname="chatbotdb",
    user="tu_usuario",
    password="tu_password",
    host="localhost",
    port="5432"
)

# Supongamos que tenés un procesador con preguntas cerradas
from tu_script_de_procesamiento import procesador

for pregunta in procesador.preguntas_cerradas:
    guardar_pregunta_en_db(pregunta, conn)

conn.close()

#procesamiento general
def procesar_todo(preguntas_cerradas, conn):
    with conn:
        with conn.cursor() as cursor:
            for pregunta in preguntas_cerradas:
                id_pregunta = insertar_pregunta(cursor, pregunta)
                
                for url in pregunta.attachments:
                    insertar_adjunto(cursor, url, id_pregunta)
                
                for respuesta in pregunta.respuestas:
                    id_respuesta = insertar_respuesta(cursor, respuesta, id_pregunta)
                    
                    for url in respuesta.attachments:
                        insertar_adjunto(cursor, url, id_respuesta)


#uso real
conn = psycopg2.connect(
    dbname='tu_db',
    user='tu_usuario',
    password='tu_password',
    host='localhost',
    port=5432
)

procesar_todo(procesador.preguntas_cerradas, conn)
conn.close()