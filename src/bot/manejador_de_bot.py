import discord
from discord.ext import commands  # permite usar comandos con prefijo (como !ayuda)
from dotenv import load_dotenv  # para cargar variables de entorno desde un archivo .env
import os  # para acceder a variables de entorno del sistema
import logging  # para registrar mensajes en un archivo de log
from utils_for_all.utilidades_logs import setup_logger,LOG_DIR_ABS
from datetime import datetime

class DiscordChatbot: # encapsula lógica del funcionamiento del chatbot
    def __init__(self):
        # Carga del entorno
        load_dotenv()  # carga las variables del archivo .env al entorno de ejecución
        self.token = os.getenv('DISCORD_TOKEN')  # obtiene el token del bot desde la variable de entorno
        self.nombre_canal_del_chatbot = os.getenv('NOMBRE_CANAL_CHATBOT')  # obtiene el nombre del canal desde .env
        self.id_canal_chatbot = os.getenv('ID_CANAL_CHATBOT')  # obtiene el ID del canal

        # Crear 2 tipos de logs: 
        # 1- el que es externo y no manejamos, popio con datos del funcionamiento de discord
        fecha_discord_log = datetime.now().strftime("log_discord_%d_%m_%y_%H_%M")
        archivo_log_discord = os.path.join(LOG_DIR_ABS, fecha_discord_log)
        self.discord_handler = logging.FileHandler(filename=archivo_log_discord, encoding='utf-8', mode='w')  # guarda logs provenientes de discord (externos)
        # 2- el que es de interno de nuestro sistema chatbot
        self.logger_chatbot_discord= setup_logger('chatbot_con_discord','log_chatbot_integracion_discord.txt')

        # Configuración de intents
        intents = discord.Intents.default()  # crea un objeto Intents con configuración básica para detectar eventos
        intents.messages = True  # permite que el bot reciba eventos de mensajes nuevos
        intents.message_content = True  # permite que el bot acceda al texto de los mensajes

        # Inicicialización del bot
        self.bot = commands.Bot(command_prefix="",intents=intents)  # crea una instancia del bot con los intents definidos
        self.setup_events()

    def setup_events(self):
        @self.bot.event  
        async def on_ready(): # mensaje que se da 1 única vez : cuando el bot se conecta a Discord y se logra la autenticación (no cada vez que se une a un servidor)
            self.logger_chatbot_discord.debug(f"✅ Bot conectado como {self.bot.user}") # mensaje que se da por consola de VS studio

            for guild in self.bot.guilds:  # recorre todos los servidores (guilds) donde está el bot (en el momento en que se autentica)
                canal = None  # inicializa la variable canal

                if self.id_canal_chatbot:  # si se definió un ID de canal
                    canal = self.bot.get_channel(int(self.id_canal_chatbot))  # obtiene el canal por ID

                if not canal and self.nombre_canal_del_chatbot:  # si no se encontró por ID, intenta por nombre
                    canal = discord.utils.get(guild.text_channels, name=self.nombre_canal_del_chatbot)  # obtiene canal por nombre

                if canal:  # si se encontró el canal
                    await canal.send(f"🤖 ¡Bot conectado como {self.bot.user}!")   # para enviar un mensaje en el canal avisando que el bot se conectó a discord, se encuentra autenticado (await: una operación de red que puede demorar)
                    self.logger_chatbot_discord.debug(f"✅ Mensaje enviado al canal #{canal.name} en {guild.name}")  # también lo informa en consola
                else:
                    self.logger_chatbot_discord.debug(f"❌ Canal no encontrado en el servidor: {guild.name}")  # muestra error si no encuentra el canal

        @self.bot.event  # evento que se ejecuta cada vez que se envía un mensaje a algún canal de algún servidor
        async def on_message(message):
            if message.author == self.bot.user:  # ignora mensajes enviados por el propio bot
                return

            canal = message.channel  # obtiene el canal desde el que se envió el mensaje

            if isinstance(canal, discord.TextChannel) and canal.name == self.nombre_canal_del_chatbot:  # si el mensaje fue en el canal principal del bot
                thread = await canal.create_thread(  # crea un hilo a partir del mensaje recibido (await porque es una operación asíncrona que puede demorar)
                    name=f"Consulta de {message.author.display_name}",  # nombre del hilo según el usuario
                    message=message,  # mensaje base del hilo
                    auto_archive_duration=60  # se archiva después de 60 min sin actividad
                )

                await canal.send(  # deja un aviso en el canal principal (operación asíncrona)
                    f"📬 Hola {message.author.mention}! Creé un hilo para tu consulta. Hacé clic en él para continuar nuestra conversación."
                )

            elif isinstance(canal, discord.Thread) and canal.parent.name == self.nombre_canal_del_chatbot:  # si el mensaje es dentro de un hilo de ese canal
                await canal.send(  # responde también dentro del hilo ()
                    "Estoy procesando tu mensaje en el hilo..."
                )

            else:  # si el mensaje viene de otro canal no relacionado
                await canal.send(  # responde diciendo que captó el mensaje
                    f"Capté un mensaje del canal: `{canal.name}`, que decía: \"{message.content}\". Estoy probando captar mensajes."
                )
            
        @self.bot.event
        async def on_disconnect():
            for guild in self.bot.guilds:
                canal = discord.utils.get(guild.text_channels, name=self.nombre_canal_del_chatbot)
                if canal:
                    try:
                        await canal.send("⚠️ El bot se ha desconectado. Puede que no responda hasta que vuelva a conectarse.")
                    except discord.errors.Forbidden:
                        self.logger_chatbot_discord.warning(f"No tengo permisos para enviar mensaje en {guild.name} #{canal.name}")

        @self.bot.event
        async def on_resumed():
            for guild in self.bot.guilds:
                canal = discord.utils.get(guild.text_channels, name=self.nombre_canal_del_chatbot)
                if canal:
                    try:
                        await canal.send("✅ El bot está nuevamente en línea.")
                    except discord.errors.Forbidden:
                        self.logger_chatbot_discord.warning(f"No tengo permisos para enviar mensaje en {guild.name} #{canal.name}")

        
    def run(self):
        self.bot.run(self.token, log_handler=self.discord_handler, log_level=logging.DEBUG)  # ejecuta el bot con el token, guardando logs en el archivo definido



