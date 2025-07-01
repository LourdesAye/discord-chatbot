import discord
from discord.ext import commands  # permite usar comandos con prefijo (como !ayuda)
from dotenv import load_dotenv  # para cargar variables de entorno desde un archivo .env
import os  # para acceder a variables de entorno del sistema
import logging  # para registrar mensajes en un archivo de log
from embeddings.crear_vectores import get_base_de_datos_vectorial
from embeddings.utilidades_vectores import responder_a_pregunta
from utils_for_all.utilidades_logs import setup_logger
import asyncio
from datetime import datetime

# Carga del entorno
load_dotenv()  # carga las variables del archivo .env al entorno de ejecución
token = os.getenv('DISCORD_TOKEN')  # obtiene el token del bot desde la variable de entorno
nombre_canal_del_chatbot = os.getenv('NOMBRE_CANAL_CHATBOT')  # obtiene el nombre del canal desde .env
id_canal_chatbot = os.getenv('ID_CANAL_CHATBOT')  # obtiene el ID del canal

# logs
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')  # guarda logs en un archivo llamado discord.log

intents = discord.Intents.default()  # crea un objeto Intents con configuración básica para detectar eventos
intents.messages = True  # permite que el bot reciba eventos de mensajes nuevos
intents.message_content = True  # permite que el bot acceda al texto de los mensajes

bot = commands.Bot(command_prefix="!", intents=intents)  # crea una instancia del bot con prefijo "!" y los intents definidos

# 🔁 Base vectorial global
base_vectorial = None

# 🔁 Refresca la base cada 10 minutos
async def refrescar_base_vectorial_periodicamente(intervalo_min=10):
    global base_vectorial
    while True:
        await asyncio.sleep(intervalo_min * 60)
        print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Refrescando base vectorial...")
        try:
            nueva_base = get_base_de_datos_vectorial()
            if nueva_base is not None:
                base_vectorial = nueva_base
                print(f"✅ Base vectorial actualizada a las {datetime.now().strftime('%H:%M:%S')}")
            else:
                print("⚠️ No se encontró contenido nuevo para actualizar la base.")
        except Exception as e:
            print(f"❌ Error al refrescar la base vectorial: {e}")

@bot.event  # evento que se dispara cuando el bot está listo y conectado
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")  # mensaje en consola para confirmar conexión

    # Lanzamos tarea en segundo plano
    bot.loop.create_task(refrescar_base_vectorial_periodicamente(10))
    print("📚 Base vectorial cargada.")
    

    for guild in bot.guilds:  # recorre todos los servidores (guilds) donde está el bot
        canal = None  # inicializa la variable canal

        if id_canal_chatbot:  # si se definió un ID de canal
            canal = bot.get_channel(int(id_canal_chatbot))  # busca el canal por ID

        if not canal and nombre_canal_del_chatbot:  # si no se encontró por ID, intenta por nombre
            canal = discord.utils.get(guild.text_channels, name=nombre_canal_del_chatbot)  # busca canal por nombre

        if canal:  # si se encontró el canal
            await canal.send(f"🤖 ¡Bot conectado como {bot.user}!")   # para enviar un mensaje en el canal avisando que el bot está online (await: una operación de red que puede demorar)
            print(f"✅ Mensaje enviado al canal #{canal.name} en {guild.name}")  # también lo informa en consola
        else:
            print(f"❌ Canal no encontrado en el servidor: {guild.name}")  # muestra error si no encuentra el canal

@bot.event  # evento que se ejecuta cada vez que se envía un mensaje
async def on_message(message):
    if message.author == bot.user:  # ignora mensajes enviados por el propio bot
        return

    canal = message.channel  # obtiene el canal desde el que se envió el mensaje

    if isinstance(canal, discord.TextChannel) and canal.name == nombre_canal_del_chatbot:  # si el mensaje fue en el canal principal del bot
        thread = await canal.create_thread(  # crea un hilo a partir del mensaje recibido (await porque es una operación asíncrona que puede demorar)
            name=f"Consulta de {message.author.display_name}",  # nombre del hilo según el usuario
            message=message,  # mensaje base del hilo
            auto_archive_duration=60  # se archiva después de 60 min sin actividad
        )

        aviso = await thread.send("⌛ Pensando una respuesta para vos...")

        global base_vectorial
        texto_pregunta = message.content.strip()
        respuesta = responder_a_pregunta(base_vectorial, texto_pregunta)

        await aviso.edit(content=respuesta)

        await canal.send(  # deja un aviso visible en el canal principal (operación asíncrona)
            f"📬 Hola {message.author.mention}! Creé un hilo para tu consulta. Hacé clic en él para continuar nuestra conversación."
        )

    elif isinstance(canal, discord.Thread) and canal.parent.name == nombre_canal_del_chatbot:  # si el mensaje es dentro de un hilo de ese canal
        await canal.send(  # responde también dentro del hilo ()
            "Estoy procesando tu mensaje en el hilo..."
        )

    else:  # si el mensaje viene de otro canal no relacionado
        await canal.send(  # responde diciendo que captó el mensaje
            f"Capté un mensaje del canal: `{canal.name}`, que decía: \"{message.content}\". Estoy probando captar mensajes."
        )
    

bot.run(token, log_handler=handler, log_level=logging.DEBUG)  # ejecuta el bot con el token, guardando logs en el archivo definido



