# --- Utilidades ---

def primeras_cinco_palabras(texto):
    return ' '.join(texto.split()[:5])

def contar_palabras(texto):
    return len(texto.split())

# --- Reglas y configuración ---

FRASES_CLAVE_PREGUNTAS = [
    "c\u00f3mo", "cu\u00e1ndo", "qu\u00e9", "cu\u00e1l", "d\u00f3nde", "por qu\u00e9", "para qu\u00e9",
    "qu\u00e9 pasa si", "tengo una consulta", "tengo una duda", "tengo una pregunta",
    "mi duda es", "mi consulta es", "quisiera consultar", 
    "quer\u00eda saber si", "me surgi\u00f3 la duda", "necesito saber si", "me pregunto si",
    "alguien sabe", "una duda", "una consulta","necesito ayuda", "es posible", "qu\u00e9 deber\u00eda",
    "que deber\u00eda", "duda diferente","otro problema"
]

FRASES_CIERRE_DOCENTE = ["perfecto", "exacto", "buen\u00edsimo"]
FRASES_CIERRE_ALUMNOS = ["gracias", "perfecto", "buen\u00edsimo", "genial", "muchas gracias",
                          "joya", "much\u00edsimas gracias", "oka", "ok"]

MAX_CARACTERES_RESP_CORTA = 14
MAX_PALABRAS_PREGUNTA_SIN_CONTEXTO = 6

FRASES_ADMINISTRATIVAS = ["hacerlo de forma individual","que version de java tenemos que usar", " nos pueden pasar su link del repositorio para poder corregirles",
                          "entrega de la tarea","ayudante asignado para el tp","como exportamos el diagrama de clase",
                          "el repo para el TPA","se podría pedir un canal de voz","estaban mal los permisos","nos toco corregir tu tp",
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
                          "a los que vamos al recu","el cronograma dice que","corrigen ahi mismo", "voy a recuperar",
                          "los enunciados de los recuperatorios de estas últimas 2 fechas están subidos en algún lado?",
                          "en su momento no pude unirme al repo de mi grupo","clase de consulta antes del final",
                          "por casualidad grabaciones d clases de años anteriores hay", "felices pascuas",
                          "el mismo sábado sería la colecta de juguetes","hoy es en medrano?","esta bien subido asi",
                          "quería avisar que no voy a poder estar en la clase de hoy", "hoy no hay clase?","@690329080750669925",
                          "mañana hay clase? pregunto por el paro", "en qué fecha serían los recuperatorios de febrero",
                          "consulta, el aula es la de siempre 277? o la 4?","en el aula virtual ya se encuentra disponible la práctica 2",
                          "aquellos que estamos en situacion de rendir final, vamos a poder anotarnos para rendirlo este sabado 7/12",
                          "tendrias el link ? por que no lo encuentro","en la lista de alumnos me figura otro mail",
                          " estaba revisando el cronograma para este jueves", " quien entregó también solo la primera parte",
                          "en la entrega del aula menciona que agregremos todo","consulta que es mas personal", "alumnos que no aparecíamos en las actas?",
                          "tenemos que corregir su tp","corregir el tp","me pasa el link del repo","corregir su tp",
                          "hay algún apunte para leer antes de la clase de hoy","estoy con faringo-amigdalitis", "hoy cursamos en el aula",
                          "cosa que vi en el campus para editar","no esté subida la clase de este miércoles","si alguien sabe dónde están ",
                          "las actividades de mañana son grupales"," votamos todos los miembros del grupo",
                          "yo mañana trabajo y no puedo ir a la clase","los temas que entran al segundo parcial",
                          "tiempo en la corrección de las notas","fechas de recuperacion para febrero","ya tengo acceso al repo de alguna manera",
                          "si nos presentamos a una fecha de recuperación","fechas de primeros y segundos recuperatorios",
                          " los recuperatorios van a ser en fechas de finales", "no puedo ir por temas familiares",
                          "las fechas de los recuperatorios también coinciden con las fechas de los finales de diseño",
                          "formulario para atender el recuperatorio","fechas de primeros y segundos recuperatorios",
                          "está disponible el repositorio del ejercicio del seminario", "la clase de consultas va a estar grabada",
                          "yo aprobo el primer parcial y el parte de persistencia de segundo parcial", "n el caso que tenga que recuperar los dos parciales"
                          "cuando va a ser la fecha de recuperatorio del primer parcial", "para el parcial la teoría que podemos llevar tiene que ser si o si",
                          "no pude entrar a la clase de consultas","no encuetro mi cuaderno", " manera de descargar el der del seminario",
                          "no pude entrar a la clase de consultas","cuando va a ser la fecha de recuperatorio del primer parcial",
                          "podrías pasar la clave del zoom nuevamente?","cuando puedan nos podrian pasar porfas la grabacion de la clase",
                          "si es posible que puedan pasar el enunciado del recuperatorio de arquitectura del sabado pasado",
                          "donde puedo conseguir ese resumen","entiendo que ya lo levanta no","mañana 9:30 para el recu",
                          "enunciado del final del sabado pasado","material de lectura recomendada para mañana", "falta una hoja",
                          "el miercoles envian por mail el contexto general del final del jueves","ya esta subido a algún lado el resumen",
                          "llevar hojas tamaño oficio para hacer el diagrama","la modalidad de la clase de mañana", "en qué aula es el recuperatorio",
                          " el repo par el tpa lo creamos nosotros","iban a subir el código","quedo grabada esa clase",
                          "la clase de consulta de ayer está subida","la entrega del 11 de septiembre serían las entregas 4 y 5 de los enunciados",
                          "nuestro ayudante dijo no corrigió nuestros exámenes","las grabación de la clase","la clase pre-final de esta semana quedó grabada"]

