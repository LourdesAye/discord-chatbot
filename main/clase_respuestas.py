from main.clase_mensajes import Mensaje

MAX_CANT_PALABRAS_RESPUESTA_CORTA = 10
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
        # Normalizar: quitar espacios y pasar a minúsculas
        respuesta = self.contenido.strip().lower()
        # Separación por espacios en blanco y contar palabras
        cantidad_palabras = len(respuesta.split())
        # Retorna True si la cantidad de palabras es menor o igual al límite
        return cantidad_palabras <= MAX_CANT_PALABRAS_RESPUESTA_CORTA
    
    def marcar_como_corta(self):
        if self.es_respuesta_corta():
            self.marcar_es_corta()



        