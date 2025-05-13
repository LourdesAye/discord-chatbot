from main.clase_mensajes import Mensaje

class Respuesta:
    def __init__(self, mensaje:Mensaje):
        self.id_respuesta = mensaje.id
        self.autor = mensaje.autor
        self.contenido = mensaje.contenido
        self.timestamp = mensaje.timestamp
        self.attachments= mensaje.attachments
        self.origen = mensaje.origen
        self.es_validada = False
    

    def validar(self):
        self.es_validada=True


        