from clase_respuestas import Respuesta 
from clase_mensajes import Mensaje

# lista de docentes
docentes = ["ezequieloescobar", "aylenmsandoval", "lucassaclier", "facuherrera_8", "ryan129623"]

class Pregunta:
    def __init__(self, mensaje: Mensaje):
        self.id_pregunta = mensaje.id
        self.autor = mensaje.autor
        self.contenido = mensaje.contenido
        self.timestamp = mensaje.timestamp
        self.attachments = mensaje.attachments
        self.respuestas = []
        self.cerrada = False

    def verificar_validez(respuesta: Respuesta):
        if respuesta.autor in docentes:
            respuesta.validar()

    def agregar_respuesta(self, respuesta: Respuesta):
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

    
