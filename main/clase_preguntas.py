from main.clase_respuestas import Respuesta 
from main.clase_mensajes import Mensaje
from main.clase_autores import docentes

frases_administrativas = ["hacerlo de forma individual","que version de java tenemos que usar",
                          "entrega de la tarea","ayudante asignado para el tp","como exportamos el diagrama de clase",
                          "el repo para el TPA","se podría pedir un canal de voz","estaban mal los permisos",
                          "no tengo acceso al repositorio del TPA", "usuario de github","se puede hacer de a 3",
                          "tenemos clases","entrega del tp", "a qué hora empezaría mañana", "el tp es obligatorio?",
                          "la clase es presencial"]

# ¿¿¿ por qué self en todas las definiciones de los métodos ??? 
# En Python, todos los métodos de instancia deben tener self como primer parámetro para poder acceder 
# a los atributos del objeto actual.

MAX_CANT_PALABRAS_PREGUNTA_SIN_CONTEXTO = 6

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
        self.sin_contexto = False
        self.es_administrativa = False

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
    
    def es_sin_contexto(self):
        self.sin_contexto = True

    def marcar_estado_adminsitrativa(self):
        self.es_administrativa = True

    def marcar_administrativa(self):
        mensaje = self.contenido.lower().strip() # al contenido se lo pone en minúscula y se le quitan los espacios iniciales y finales
        # Recorremos cada frase y verificamos si está en el mensaje
        for frase in frases_administrativas:
            frase_normalizada = frase.lower().strip()
            if frase_normalizada in mensaje:
                self.marcar_estado_adminsitrativa()
    
    def es_pregunta_corta(self):
        # Normalizar: quitar espacios y pasar a minúsculas
        pregunta = self.contenido.strip().lower()
        # Separación por espacios en blanco y contar palabras
        cantidad_palabras = len(pregunta.split())
        # Retorna True si la cantidad de palabras es menor o igual al límite
        return cantidad_palabras <= MAX_CANT_PALABRAS_PREGUNTA_SIN_CONTEXTO
    
    def marcar_sin_contexto(self):
        if self.es_pregunta_corta():
            self.es_sin_contexto()
    
 


    




    
