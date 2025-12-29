# ESTRUCTURAS BASES PARA CLASIFICAR MENSAJES + funciones auxiliares +  CLASE MENSAJE 
from database.models.clase_autores import lista_docentes
import os
import re
from utils.utilidades_logs import setup_logger
from database.models.utilidades_modelo_dominio import FRASES_CLAVE_PREGUNTAS,FRASES_CIERRE_ALUMNOS,FRASES_CIERRE_DOCENTE,contar_palabras,primeras_cinco_palabras

class Mensaje:
    def __init__(self, id_mensaje, autor, contenido, timestamp,attachments,origen):
        self.id_mensaje_base_de_datos= None  # se asigna al guardar en la base de datos
        self.id_mensaje_discord = id_mensaje.lower().strip()
        self.autor = autor.lower().strip()
        self.contenido = contenido.lower().strip()
        self.timestamp = timestamp.lower().strip()
        self.attachments = attachments
        self.origen = origen

    @classmethod # para indicar que es un método de clase, afecta a la clase no a la instancia
    def from_dataframe_row(cls, row, ruta_json): # 'cls' es la clase, es como self para una instancia
        #se crea una nueva instancia de la clase usando una fila (row) (objeto serie) de un DataFrame como fuente de datos.
        return cls(   # Esto llama al constructor de la clase (es como hacer Clase(...)) para crear una nueva instancia.
            id_mensaje_discord=row["id"], # row es un objeto serie, que se accede de forma similar a un diccionario, pero no lo es
            autor=row["author"],
            contenido=row["content"],
            timestamp=row["timestamp"],
            attachments=cls._procesar_attachments(row.get("attachments", [])), # Busca "attachments" en el diccionario row. Si existe, devuelve su valor sino [] (una lista vacía).
            origen=ruta_json)
    
    @classmethod
    def from_discord(cls, discord_message):
        """
        Construye un Mensaje partiendo del objeto `message` de discord.py.
        el atributo message.attachments en discord.py es una lista de objetos discord.Attachment.
        Cada elemento de esa lista representa un archivo adjunto en el mensaje, y puedes acceder a sus propiedades como:
            attachment.id: el ID único del adjunto
            attachment.filename: el nombre del archivo (nombre_archivo.extension)
            attachment.url: la URL para descargar el archivo
        """
        # Lista para guardar nombres de archivos adjuntos
        attachments = []
        try: # algunos mensajes pueden no tener attachments
            # ejemplo de attachments:
                #  [<Attachment 
                # id=1426312557093978203 
                # filename='refelxion_uso_de_herrameintas_en_tic_y_general.docx' 
                # url='refelxion_uso_de_herrameintas_en_tic_y_general.docx'>, 
                # <Attachment 
                # id=1426312557450498140 
                # filename='Charlas_empleab_ilidad_utn_frba_2_oct.docx' 
                # url='Charlas_empleab_ilidad_utn_frba_2_oct.docx'>]
            for a in discord_message.attachments: 
                # ejemplo de filename: Charlas_empleab_ilidad_utn_frba_2_oct.docx
                filename = getattr(a, "filename", str(a))
                # "Mi nombre es Lourdes".split(' ') -> ['Mi', 'nombre', 'es', 'Lourdes']
                # ejemplo de ext: docx
                ext = filename.split('.')[-1] if '.' in filename else ''
                attachments.append((filename, ext)) # agrega una tupla (nombre,extensión) a la lista
        except Exception:
        # si no tiene attachments o estructura diferente, dejamos lista vacía
            attachments = []

        autor = discord_message.author.name if hasattr(discord_message.author, 'name') else str(discord_message.author)

        return cls(
        id_mensaje_discord=str(discord_message.id),
        autor=autor,
        contenido=discord_message.content,
        timestamp=discord_message.created_at.isoformat() if hasattr(discord_message, 'created_at') else "",
        attachments=attachments,
        origen="discord_tiempo_real",
        )

    
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
