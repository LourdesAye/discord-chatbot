# ESTRUCTURAS BASES PARA CLASIFICAR MENSAJES + funciones auxiliares +  CLASE MENSAJE 
import os
# lista de docentes
docentes = ["ezequieloescobar", "aylenmsandoval", "lucassaclier", "facuherrera_8", "ryan129623","facundopiaggio","valentinaalberio"]

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
        self.id = id_mensaje
        self.autor = autor
        self.contenido = contenido
        self.timestamp = timestamp
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

    
    def es_autor_docente(self) -> bool:
        return self.autor.lower() in docentes

    def es_pregunta(self):
        texto = self.contenido.lower().strip() # convierte el mensaje que esta en texto para pasarlo a minúscula y le quita los espacios que pueda tener al incio y al final

        # Si contiene signos de interrogación es pregunta
        if "?" in texto or "¿" in texto:
            return True

        # Si contiene alguna frase típica
        for frase in frases_claves_preguntas:
            if frase.lower() in texto:
                return True

        return False
    
    def es_pregunta_reconocida_manual(self):
        frase_detectada_pregunta_manual = ["duda diferente","otro problema"]
        texto = self.contenido.lower().strip() # convierte el mensaje que esta en texto para pasarlo a minúscula y le quita los espacios que pueda tener al incio y al final
          # Si contiene alguna frase típica
        for frase in frase_detectada_pregunta_manual:
            if frase.lower() in texto.lower():
                return True
        return False
            

    def es_cierre_alumno(self):
        mensaje= self.contenido.lower().strip()
        cant_palabras=contar_palabras(mensaje)
        # Analiza si las primeras 5 palabras pueden ser una frase de cierre de alumno
        if (cant_palabras <= 5):
            for frase in frases_cierre_alumnos:
                if frase in mensaje:
                    return True
            return False
        else:
            return False
    
    
    def es_cierre_docente(self):
        # Analiza si el contenido es una frase de cierre (genial, joya, gracias, etc.)
        mensaje= self.contenido.lower().strip()
        inicio_mensaje = primeras_cinco_palabras(mensaje)
        # Analiza si las primeras 5 palabras pueden ser una frase de cierre de alumno
        for frase in frases_cierre_alumnos:
            if frase in inicio_mensaje:
                return True
        return False
