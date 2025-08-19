import os
import requests
from dotenv import load_dotenv
from utils_for_all.utilidades_logs import setup_logger

# Crear log
logger_bot_controlador = setup_logger("bot_controlado","registros_bot_controlador.txt")

# Cargar variables de entorno
load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL") # toma el webhook del archivo .env
AVATAR_URL = os.getenv("WEBHOOK_AVATAR_URL")  # opcional, URL del avatar para el bot que controla
IMAGEN_URL = os.getenv("WEBHOOK_IMAGEN_URL")  # opcional, URL de la imagen para agregarla junto al mensaje

# Simulando caida del chatbot (se debe ejecutar manualmente, se automatizará esté desplegado en un servidor (en producción) y se tenga UptimeRobot o un endpoint de status)
# Para que UptimeRobot funcione, el chatbot necesita un endpoint accesible desde internet (una URL pública), 
# porque UptimeRobot hace “pings” HTTP. Eso no se puede hacer desde tu PC local 
# salvo que uses herramientas como ngrok que crean temporalmente esa URL pública (pero expone tu computadora!).
def enviar_alerta(mensaje: str):

    if not WEBHOOK_URL:
        logger_bot_controlador.debug("⚠️ WEBHOOK_URL no definida en el .env")
        return

    data = {
        "username": "MonitorBot", # Nombre que aparecerá como remitente 
        "content": mensaje,  # Mensaje a mostrar en pantalla 
    }

    # Avatar opcional, si esta definido en el .env
    if AVATAR_URL:
        data["avatar_url"] = AVATAR_URL

    # Imagen opcional que acompañará al mensaje    
    if IMAGEN_URL:
        # Embed correcto para que Discord lo muestre
        # embed: estructura que permite agregar a la respuesta del bot imagenes, colores, títulos , entre otros, no solo texto
        data["embeds"] = [{
            "image": {"url": IMAGEN_URL}
        }]

    try: # requests.post: para enviar información a un servidor (como un webhook). Si todo sale bien, status_code será 204 (sin contenido, pero exitoso).
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code != 204:
            logger_bot_controlador.debug(f"⚠️ Webhook respondió con {response.status_code}, {response.text}")
    except Exception as e:
        logger_bot_controlador.debug(f"Error enviando alerta: {e}")
