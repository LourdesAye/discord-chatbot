# ESTRUCTURAS BASES PARA CLASIFICAR MENSAJES + funciones auxiliares +  CLASE MENSAJE 

# lista de docentes
docentes = ["ezequieloescobar", "aylenmsandoval", "lucassaclier"]

# lista de frases comunes para detectar preguntas explícitas o implícitas
frases_claves_preguntas = [
    "cómo", "cuándo", "qué", "cuál", "dónde", "por qué", "para qué",
    "qué pasa si", "tengo una consulta", "tengo una duda", "tengo una pregunta",
    "mi duda es", "mi consulta es", "quisiera consultar", 
    "quería saber si", "me surgió la duda", "necesito saber si", "me pregunto si",
    "alguien sabe", "una duda", "una consulta","necesito ayuda", "es posible"
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
    def __init__(self, id_mensaje, autor, contenido, timestamp,attachments):
        self.id = id_mensaje
        self.autor = autor
        self.contenido = contenido
        self.timestamp = timestamp
        self.attachments = attachments

    @classmethod # para indicar que es un método de clase, afecta a la clase no al objeto necesariamente
    def from_dataframe_row(cls, row): # Usamos 'cls' para referirnos a la clase, es como self para una instancia u objeto
        # Aquí estamos creando un objeto Mensaje usando los datos de la fila
        return cls(  
            id_mensaje=row["id"],
            autor=row["autor"],
            contenido=row["contenido"],
            timestamp=row["timestamp"],
            attachments=row.get("attachments", []))

    def es_autor_docente(self) -> bool:
        return self.autor.lower() in docentes
   
    def es_pregunta(self):
        texto = self.contenido.lower().strip() # convierte el mensaje que esta en texto para pasarlo a minúscula y le quita los espacios que pueda tener al incio y al final

        # Si contiene signos de interrogación es pregunta
        if "?" in texto or "¿" in texto:
            return True

        # Si contiene alguna frase típica
        for frase in frases_claves_preguntas:
            if frase in texto:
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
