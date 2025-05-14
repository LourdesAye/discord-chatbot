from main.clase_mensajes import Mensaje

MAX_CANT_CARACTERES_RESP_CORTA = 14

class Respuesta:
    def __init__(self, mensaje:Mensaje):
        self.id_respuesta = mensaje.id
        self.autor = mensaje.autor
        self.contenido = mensaje.contenido
        self.timestamp = mensaje.timestamp
        self.attachments= mensaje.attachments
        self.origen = mensaje.origen
        self.es_validada = False
        self.es_corta= False
    

    def validar(self):
        self.es_validada=True

    def marcar_es_corta(self):
        self.es_corta= True
    
    def es_respuesta_corta(self):
        # Normalizar: quitar espacios al inicio y al final, y pasar a minúsculas
        respuesta = self.contenido.strip().lower()
        cantidad_caracteres = len(respuesta)
        # Retorna True si la cantidad de palabras es menor o igual al límite
        return cantidad_caracteres <= MAX_CANT_CARACTERES_RESP_CORTA
    
    def marcar_como_corta(self):
        if self.es_respuesta_corta():
            self.marcar_es_corta()



        