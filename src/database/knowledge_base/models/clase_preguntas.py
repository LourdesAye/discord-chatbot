from database.knowledge_base.models.clase_respuestas import Respuesta 
from database.knowledge_base.models.clase_mensajes import Mensaje
from database.knowledge_base.models.clase_autores import docentes
from database.knowledge_base.utils.utilidades_conversiones import convertir_a_datetime

frases_administrativas = ["hacerlo de forma individual","que version de java tenemos que usar",
                          "entrega de la tarea","ayudante asignado para el tp","como exportamos el diagrama de clase",
                          "el repo para el TPA","se podría pedir un canal de voz","estaban mal los permisos",
                          "no tengo acceso al repositorio del TPA", "usuario de github","se puede hacer de a 3",
                          "tenemos clases","entrega del tp", "a qué hora empezaría mañana", "el tp es obligatorio?",
                          "la clase es presencial","el repo para el TPA","no pude acceder al repo del equipo",
                          "a que hora se toman","que significa el pendiente en la parte de teoria", "para promocionar",
                          "no esten todas las PPTS","a qué hora","a que hora","me quiero inscribir al final",
                          "doy mi presente a la noche","no encuentro mi cuaderno","a qué hora hay que estar mañana",
                          "voy a recuperar","cual es el horario","certificado de asistencia al parcial",
                          "si tengo para recuperar","en caso de que tenga que recuperar","consulta sobre los recus",
                          "voy a recuperar","puedo recuperar","el parte teorico tmb sera parte del recuperatorio",
                          "creamos 1 solo repositorio","que temas se trataron el dia","podre usar vue para el maquetado",
                          "a los que vamos al recu","el cronograma dice que","corrigen ahi mismo",
                          "los enunciados de los recuperatorios de estas últimas 2 fechas están subidos en algún lado?",
                          "en su momento no pude unirme al repo de mi grupo","clase de consulta antes del final",
                          "por casualidad grabaciones d clases de años anteriores hay", "felices pascuas",
                          "el mismo sábado sería la colecta de juguetes","hoy es en medrano?","esta bien subido asi",
                          "quería avisar que no voy a poder estar en la clase de hoy", "hoy no hay clase?",
                          "mañana hay clase? pregunto por el paro", "en qué fecha serían los recuperatorios de febrero",
                          "consulta, el aula es la de siempre 277? o la 4?","en el aula virtual ya se encuentra disponible la práctica 2",
                          "aquellos que estamos en situacion de rendir final, vamos a poder anotarnos para rendirlo este sabado 7/12",
                          "tendrias el link ? por que no lo encuentro","en la lista de alumnos me figura otro mail",
                          " estaba revisando el cronograma para este jueves", " quien entregó también solo la primera parte",
                          "en la entrega del aula menciona que agregremos todo","consulta que es mas personal", "alumnos que no aparecíamos en las actas?",
                          "tenemos que corregir su tp","corregir el tp","me pasa el link del repo","corregir su tp",
                          "hay algún apunte para leer antes de la clase de hoy","estoy con faringo-amigdalitis", "hoy cursamos en el aula",
                          "cosa que vi en el campus para editar","no esté subida la clase de este miércoles",
                          "las actividades de mañana son grupales"]

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
        return self.cerrada
    
    def tiene_mismo_autor(self,mensaje: Mensaje):
        return self.autor== mensaje.autor
    
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
        # Recorremos cada frase y verificamos si está en el mensaje
        for frase in frases_administrativas:
            frase_normalizada = frase.lower().strip() # se ponen en minúscula y sin espacios iniciales y finales cada frase de la lista
            if frase_normalizada in self.contenido:
                self.marcar_estado_adminsitrativa()
    
    def es_pregunta_corta(self):
        # Separación por espacios en blanco y contar palabras
        cantidad_palabras = len(self.contenido.split())
        # Retorna True si la cantidad de palabras es menor o igual al límite
        return cantidad_palabras <= MAX_CANT_PALABRAS_PREGUNTA_SIN_CONTEXTO
    
    def marcar_sin_contexto(self):
        if self.es_pregunta_corta():
            self.es_sin_contexto()
    
    def obtener_ultima_respuesta_no_docente(self,mensaje:Mensaje):
        for respuesta in reversed(self.respuestas):
            if respuesta.autor not in docentes:
                 if respuesta.autor != mensaje.autor:
                     if self.puede_ser_respuesta_validada(respuesta):
                         return respuesta
        return None
    
    def puede_ser_respuesta_validada(self, respuesta:Respuesta) -> bool:
        # Frases vacías o irrelevantes
        if not respuesta.contenido or respuesta.contenido in {"hola", "hola buenas tardes", "gracias", "perfecto", "solucionado", "dale", "sisi", "sí", "si", "ok"}:
            return False
        # Frases muy cortas que suelen ser de cierre o sin información útil
        if len(respuesta.contenido.split()) <= 3:
            return False
        return True
    
    def tiene_respuesta_validada(self):
        # any devuelve true si al menos un elemento de la lista cumple la condición
        # no hay problema con lista vacia: devuelve false si es asi
        return any(respuesta.es_validada for respuesta in self.respuestas)
    
    def es_cercana_en_tiempo(self, mensaje:Mensaje, max_delta_segundos):
       fecha_mensaje= convertir_a_datetime(mensaje.timestamp)
       fecha_pregunta = convertir_a_datetime(self.timestamp)
       return (fecha_mensaje -fecha_pregunta).total_seconds() < max_delta_segundos

