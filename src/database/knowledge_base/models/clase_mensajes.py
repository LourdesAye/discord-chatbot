# ESTRUCTURAS BASES PARA CLASIFICAR MENSAJES + funciones auxiliares +  CLASE MENSAJE 
from database.knowledge_base.models.clase_autores import lista_docentes
import os
import re
from utils_for_all.utilidades_logs import setup_logger
from database.knowledge_base.models.utilidades_modelo_dominio import FRASES_CLAVE_PREGUNTAS,FRASES_CIERRE_ALUMNOS,FRASES_CIERRE_DOCENTE,contar_palabras,primeras_cinco_palabras

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
            id_mensaje=row["id"], # row es un objeto serie, que se accede de forma similar a un diccionario, pero no lo es
            autor=row["author"],
            contenido=row["content"],
            timestamp=row["timestamp"],
            attachments=cls._procesar_attachments(row.get("attachments", [])), # Busca "attachments" en el diccionario row. Si existe, devuelve su valor sino [] (una lista vacía).
            origen=ruta_json)
    
    @staticmethod # para indicar que es un método de clase, afecta a la clase no al objeto necesariamente
    def _procesar_attachments(lista_adjuntos):
        # os.path.basename(ruta) : "1223680537604915200_image.png" para obtener solo el nombre del archivo sin la ruta completa.
        # split(".")[-1] : separar tipo de archivo del nombre : png
        return [(os.path.basename(a), os.path.basename(a).split(".")[-1]) for a in lista_adjuntos]


    def contiene_frase_clave(self):
        # si dentro en el contenido del mensaje esta la frase exacta incluida tenga mayusculas o minúsculas
        return any( re.search( rf"\b{re.escape(f)}\b", self.contenido, flags=re.IGNORECASE) for f in FRASES_CLAVE_PREGUNTAS)
        
            
    def contiene_signo_interrogacion(self):
        return "?" in self.contenido or "\u00bf" in self.contenido # ¿ es "\u00bf"

    def es_autor_docente(self) -> bool:
        return self.autor in lista_docentes

    def es_pregunta(self):
        return self.contiene_signo_interrogacion() or self.contiene_frase_clave()
            

    def es_cierre_alumno(self):
        # Analiza si las primeras 5 palabras pueden ser una frase de cierre de alumno
        return contar_palabras(self.contenido) <= 5 and any(f in self.contenido for f in FRASES_CIERRE_ALUMNOS)
    
    
    def es_cierre_docente(self): 
        # Analiza si el contenido es una frase de cierre (genial, joya, gracias, etc.) por parte del docente
        inicio = primeras_cinco_palabras(self.contenido) # Analiza si las primeras 5 palabras pueden ser una frase de cierre del docente
        return any(f in inicio for f in FRASES_CIERRE_DOCENTE)
