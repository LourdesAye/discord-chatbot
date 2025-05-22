# ESTRUCTURAS BASES PARA CLASIFICAR MENSAJES + funciones auxiliares +  CLASE MENSAJE 
from database.knowledge_base.models.clase_autores import docentes
import os
import re

# lista de frases comunes para detectar preguntas explícitas o implícitas
frases_claves_preguntas = [
    "cómo", "cuándo", "qué", "cuál", "dónde", "por qué", "para qué",
    "qué pasa si", "tengo una consulta", "tengo una duda", "tengo una pregunta",
    "mi duda es", "mi consulta es", "quisiera consultar", 
    "quería saber si", "me surgió la duda", "necesito saber si", "me pregunto si",
    "alguien sabe", "una duda", "una consulta","necesito ayuda", "es posible", "qué debería", "que debería",
    "duda diferente","otro problema"
]

# lista de mensajes de cierre de docentes
frases_cierre_docente =["perfecto", "exacto","buenísimo"]

# lista de mensajes de cierre de alumnos
frases_cierre_alumnos = ["gracias","perfecto","buenísimo","genial",
                         "muchas gracias","joya","genial","muchísimas gracias","oka","ok"]

def primeras_cinco_palabras(texto):
    palabras = texto.split()
    return ' '.join(palabras[:5])

def contar_palabras(texto):
      palabras = texto.split()
      return len(palabras)

class Mensaje:
    def __init__(self, id_mensaje, autor, contenido, timestamp,attachments,origen):
        self.id = id_mensaje.lower().strip()
        self.autor = autor.lower().strip()
        self.contenido = contenido.lower().strip()
        self.timestamp = timestamp.lower().strip()
        self.attachments = attachments
        self.origen = origen

    @classmethod # para indicar que es un método de clase, afecta a la clase no a la instancia
    def from_dataframe_row(cls, row, ruta_json): # 'cls' es la clase, es como self para una instancia
        #se crea una nueva instancia de la clase usando una fila (row) (objeto serie) de un DataFrame como fuente de datos.
        return cls(   # Esto llama al constructor de la clase (es como hacer Clase(...)) para crear una nueva instancia.
            id_mensaje=row["id"].lower().strip(), # row es un objeto serie, que se accede de forma similar a un diccionario, pero no lo es
            autor=row["author"].lower().strip(),
            contenido=row["content"].lower().strip(),
            timestamp=row["timestamp"].lower().strip(),
            attachments=cls.procesar_attachments(row.get("attachments", [])), # Busca "attachments" en el diccionario row. Si existe, devuelve su valor sino [] (una lista vacía).
            origen=ruta_json)
    
    @staticmethod # para indicar que es un método de clase, afecta a la clase no al objeto necesariamente
    def procesar_attachments(lista_adjuntos_json):
        resultado = []
        for ruta in lista_adjuntos_json:
            nombre_archivo = os.path.basename(ruta) # "1223680537604915200_image.png" para obtener solo el nombre del archivo sin la ruta completa.
            tipo = nombre_archivo.split(".")[-1] # "png" Separa el nombre del archivo por "." y toma el último elemento ([-1]), que representa la extensión del archivo.
            resultado.append((nombre_archivo, tipo))
        return resultado # lista de tupla (nombre_archivo,tipo)

    def contiene_frase_clave(self):
        texto = self.contenido
        for frase in frases_claves_preguntas:
            if re.search(r'\b' + re.escape(frase) + r'\b', texto):
                return True
            
    def contiene_signo_interrogacion(self):
        texto = self.contenido
        if "?" in texto or "¿" in texto:
            return True

    def es_autor_docente(self) -> bool:
        return self.autor in docentes

    def es_pregunta(self):
        # si contiene signos de interrogación es pregunta
        self.contiene_signo_interrogacion()
        # si contiene alguna frase típica de consulta también es pregunta
        self.contiene_frase_clave()
        return False
            

    def es_cierre_alumno(self):
         cant_palabras=contar_palabras(self.contenido)
         # Analiza si las primeras 5 palabras pueden ser una frase de cierre de alumno
         if (cant_palabras <= 5):
             for frase in frases_cierre_alumnos:
                 if frase in self.contenido:
                     return True
             return False
         else:
             return False
    
    
    def es_cierre_docente(self): # Analiza si el contenido es una frase de cierre (genial, joya, gracias, etc.) por parte del docente
        inicio_mensaje = primeras_cinco_palabras(self.contenido) # Analiza si las primeras 5 palabras pueden ser una frase de cierre del docente
        for frase in frases_cierre_docente:
            if frase in inicio_mensaje:
                return True
        return False
