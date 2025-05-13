from main.clase_respuestas import Respuesta 
from main.clase_mensajes import Mensaje
from main.clase_autores import docentes

# ¿¿¿ por qué self en todas las definiciones de los métodos ??? 
# En Python, todos los métodos de instancia deben tener self como primer parámetro para poder acceder 
# a los atributos del objeto actual.

class Pregunta:
    def __init__(self, mensaje: Mensaje):
        self.id_pregunta = mensaje.id
        self.autor = mensaje.autor
        self.contenido = mensaje.contenido
        self.timestamp = mensaje.timestamp
        self.attachments = mensaje.attachments
        self.origen = mensaje.origen
        self.respuestas = []
        self.cerrada = False

    def verificar_validez(self,respuesta: Respuesta):
        if respuesta.autor in docentes:
            respuesta.validar()

    def agregar_respuesta(self,mensaje: Mensaje):
        respuesta= Respuesta(mensaje)
        self.respuestas.append(respuesta)
        self.verificar_validez(respuesta)

    def cerrar(self):
        self.cerrada = True
    
    def esta_cerrada(self):
        if self.cerrada is True:
            return True
        else:
            return False
    
    def tiene_mismo_autor(self,mensaje: Mensaje):
        if self.autor.lower().strip() == mensaje.autor.lower().strip():
            return True
        else:
            return False
    
    def obtener_ultima_respuesta(self):
        if self.respuestas:
         return self.respuestas[-1]
        return None
    
    def tiene_respuestas(self):
        return bool(self.respuestas)
    
    def concatenar_contenido(self, nuevo_texto):
        self.contenido = f"{self.contenido.rstrip()} {nuevo_texto.lstrip()}"
        # rstrip(): Elimina los espacios en blanco (incluyendo saltos de línea) que puedan estar al final
        # lstrip(): Elimina los espacios en blanco al inicio




    
