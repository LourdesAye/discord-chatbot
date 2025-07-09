from database.knowledge_base.models.clase_respuestas import Respuesta 
from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.utils.utilidades_conversiones import convertir_a_datetime
from database.knowledge_base.models.utilidades_modelo_dominio import MAX_PALABRAS_PREGUNTA_SIN_CONTEXTO
from database.knowledge_base.utils.utilidades_conversiones import tiempo_transcurrido,convertir_a_datetime

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

    def agregar_respuesta(self, mensaje: Mensaje, lista_docentes):
            respuesta = Respuesta(mensaje)
            if respuesta.autor in lista_docentes:
                respuesta.validar()
            respuesta.marcar_como_corta()
            self.respuestas.append(respuesta)

    def cerrar(self):
        self.cerrada = True

    def tiene_respuesta_validada(self):
        return any(r.es_validada for r in self.respuestas)

    def marcar_sin_contexto_si_corta(self):
        if len(self.contenido.split()) <= MAX_PALABRAS_PREGUNTA_SIN_CONTEXTO:
            self.sin_contexto = True

    def marcar_administrativa(self,frases_admin):
        for frase in frases_admin:
            if frase.lower() in self.contenido:
                self.es_administrativa = True
                break

    def es_extensible_con(self, mensaje,max_seg):
        return not self.respuestas and tiempo_transcurrido(convertir_a_datetime(self.timestamp), convertir_a_datetime(mensaje.timestamp)).seconds < max_seg
    
    def tiene_mismo_autor(self,mensaje: Mensaje):
        return self.autor== mensaje.autor
    
    def concatenar_contenido(self, nuevo_texto):
        self.contenido = f"{self.contenido.rstrip()} {nuevo_texto.lstrip()}"
        # rstrip(): Elimina los espacios en blanco (incluyendo saltos de línea) que puedan estar al final
        # lstrip(): Elimina los espacios en blanco al inicio
