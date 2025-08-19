import discord
from discord.ext import commands  # permite usar comandos con prefijo (como !ayuda)
from dotenv import load_dotenv  # para cargar variables de entorno desde un archivo .env
import os  # para acceder a variables de entorno del sistema
import logging  # para registrar mensajes en un archivo de log
from utils_for_all.utilidades_logs import setup_logger,LOG_DIR_ABS
from datetime import datetime
from discord import Embed, Colour
from zoneinfo import ZoneInfo

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
        async def on_ready(): # mensaje que se da cuando el bot se auetntica en discord (pasó mucho tiempo de la última conexión o comienza a funcionar) : No cada vez que se une a un servidor
            self.logger_chatbot_discord.debug(f"✅ Bot conectado como {self.bot.user}") # log que registra autenticación en Discord

            for guild in self.bot.guilds:  # recorre todos los servidores (guilds) donde está el bot (en el momento en que se autentica)
                canal = None  # inicializa la variable canal

                if self.id_canal_chatbot:  # si se definió un ID de canal
                    canal = self.bot.get_channel(int(self.id_canal_chatbot))  # obtiene el canal por ID

                if not canal and self.nombre_canal_del_chatbot:  # si no se encontró por ID, intenta por nombre
                    canal = discord.utils.get(guild.text_channels, name=self.nombre_canal_del_chatbot)  # obtiene canal de texto con cierto nombre

                if canal:  # si se encontró el canal
                    await canal.send(f"🤖 ¡Bot conectado como {self.bot.user}!")   # para enviar un mensaje en el canal avisando que el chatbot se autenticó en discord (await: una operación de red que puede demorar)
                    self.logger_chatbot_discord.debug(f"✅ Mensaje de autenticación exitosa enviado al canal #{canal.name} en {guild.name}")  # se documenta en log la acción
                else:
                    self.logger_chatbot_discord.debug(f"❌ Canal no encontrado en el servidor: {guild.name}")  # se documenta el error: no encuentra el canal

        @self.bot.event  
        async def on_message(message): # evento que se ejecuta cada vez que se envía un mensaje a algún canal de algún servidor
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

            else:
                embed = Embed(
                title="📩 ¡Mensaje nuevo capturado!",
                colour=Colour.green(),
                timestamp=message.created_at  # Discord muestra el timestamp arriba a la derecha
                )
            # 👇 Avatar a la derecha, NO usamos set_author así el título queda primero
            embed.set_thumbnail(url=message.author.display_avatar.url)

            # 1) Autor (primero, debajo del título)
            embed.add_field(
                name="👤 Autor",
                value=f"{message.author.mention}\nID: `{message.author.id}`",
                inline=False
            )

            # 2) Contenido
            embed.add_field(name="🗨️ Contenido", value=content, inline=False)

            # 3) Ubicación e IDs
            embed.add_field(name="📍 Canal", value=message.channel.name, inline=True)
            embed.add_field(name="🏠 Servidor", value=guild, inline=True)
            embed.add_field(name="🆔 ID del mensaje", value=str(message.id), inline=False)

            # 4) Tiempos
            enviado = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            editado = message.edited_at.strftime("%Y-%m-%d %H:%M:%S") if message.edited_at else "Sin editar"
            embed.add_field(name="⏰ Enviado", value=enviado, inline=True)
            embed.add_field(name="✏️ Editado", value=editado, inline=True)

            # 5) Otros detalles
            embed.add_field(name="📎 Adjuntos", value=_fmt_list(attachments), inline=False)
            embed.add_field(name="📦 Embeds", value=str(embeds_count) if embeds_count else "Ninguno", inline=True)
            embed.add_field(name="👥 Menciones", value=_fmt_list(mentions, "Ninguna", ", "), inline=False)
            embed.add_field(name="🎭 Roles", value=_fmt_list(roles, "Ninguno", ", "), inline=False)
            embed.add_field(name="😀 Stickers", value=_fmt_list(stickers), inline=False)
            embed.add_field(name="📊 Reacciones", value=_fmt_list(reactions, "Ninguna", ", "), inline=False)
            embed.add_field(name="🚩 Banderas", value=str(message.flags) if message.flags else "Ninguna", inline=False)
            embed.add_field(name="📌 Anclado", value="Sí" if message.pinned else "No", inline=True)
            embed.add_field(name="📦 Tipo", value=message.type.name, inline=True)
            embed.add_field(name="🔗 Enlace", value=message.jump_url, inline=False)





                # Capturamos los datos
                content = message.content # mensaje
                author = str(message.author) # autor
                channel = message.channel.name # nombre del canal
                guild = message.guild.name if message.guild else "DM" # nombre del servidor
                msg_id = message.id # id úncio del mensaje
                local_time = message.created_at.astimezone(ZoneInfo("America/Argentina/Buenos_Aires"))
                timestamp = local_time.strftime("%Y-%m-%d %H:%M:%S") # fecha del mensaje
                attachments = [a.url for a in message.attachments] # nombre de cada archivo adjunto
                embeds = message.embeds # lista de elementos agregados extra 
                mentions = [m.name for m in message.mentions] # menciones dentro del mensaje
                reactions = message.reactions # reacciones del mensaje
                flags = message.flags # banderas varias en discord
                pinned = message.pinned # booleano que indica si mensaje fue fijado o no en discord 
                msg_type = message.type.name # tipo de mensaje : sistema, respuesta, texto
                edited = message.edited_at.strftime("%Y-%m-%d %H:%M:%S") if message.edited_at else "Sin editar" # fecha de edición del mensaje si fue editado
                stickers = [s.name for s in message.stickers] if message.stickers else [] # nombre de stickers 
                roles = [r.name for r in message.author.roles] if hasattr(message.author, "roles") else [] # rol o roles del autor
                jump = message.jump_url # url para ir directamente al mensaje original al que se hace referencia

                # Embed que mostrará el chatbot para indicar los datos del mensaje captados en un canal por un usuario
                # (representación visual enriquecida de un mensaje que va más allá del texto simple)
                # (incluir elementos como títulos, descripciones, imágenes, campos personalizados y otros detalles que hacen que la información sea más atractiva y fácil de entender)
                embed = Embed(
                    title="📩 ¡Mensaje nuevo capturado!",
                    colour=Colour.green(), # colorea : verde
                    timestamp=message.created_at # fecha en la que fue creado el mensaje en discord
                )

                # coloca en el embed que aparecerá en discord el nombre del usuario que generó el mensaje original y su avatar
                embed.set_author(name=author, icon_url=message.author.display_avatar.url)
                # author = str(message.author) es el autor del mensaje y que aparece en la parte superior del mensaje embebido en Discord. 
                # obtiene usuario del mensaje, para captar la URL de su avatar. 

                embed.add_field(name="🧑 Autor", value=author, inline=False) # inline =True que ocupe toda una línea en el embed
                embed.add_field(name="🆔 Autor ID", value=message.author.id, inline=False)
                embed.add_field(name="📍 Canal", value=channel, inline=False)
                embed.add_field(name="🏠 Servidor", value=guild, inline=False)
                embed.add_field(name="🆔 ID del mensaje", value=msg_id, inline=False)
                embed.add_field(name="⏰ Enviado", value=timestamp, inline=False)
                embed.add_field(name="✏️ Editado", value=edited, inline=False)
                embed.add_field(name="🗨️ Contenido", value=content or "*[Vacío]*", inline=False)
                embed.add_field(name="📎 Adjuntos", value="\n".join(attachments) if attachments else "Ninguno", inline=False)
                embed.add_field(name="📦 Embeds", value=f"{len(embeds)} encontrados" if embeds else "Ninguno", inline=False)
                embed.add_field(name="👥 Menciones", value=", ".join(mentions) if mentions else "Ninguna", inline=False)
                embed.add_field(name="🎭 Roles", value=", ".join(roles) if roles else "Ninguno", inline=False)
                embed.add_field(name="😀 Stickers", value=", ".join(stickers) if stickers else "Ninguno", inline=False)
                embed.add_field(name="📊 Reacciones", value=", ".join([str(r) for r in reactions]) if reactions else "Ninguna", inline=False)
                embed.add_field(name="🚩 Banderas", value=str(flags) if flags else "Ninguna", inline=False)
                embed.add_field(name="📌 Anclado", value="Sí" if pinned else "No", inline=False)
                embed.add_field(name="📦 Tipo", value=msg_type, inline=False)
                embed.add_field(name="🔗 Enlace", value=jump, inline=False)

                if isinstance(message.channel, discord.Thread):
                    embed.add_field(name="🧵 Hilo", value=message.channel.name, inline=True)

                await message.channel.send(embed=embed)

            await self.bot.process_commands(message)
                    
        @self.bot.event
        async def on_message_edit(before: discord.Message, after: discord.Message): # Evento: cuando un mensaje es editado
            if after.author == self.bot.user:
                return

            autor = str(after.author) # autor que aplico los cambios
            canal = after.channel.name # nombre del canal
            guild = after.guild.name if after.guild else "DM" # nombre del servidor 
            timestamp = after.edited_at # fecha de edición

            # Comparaciones
            before_attachments = [a.url for a in before.attachments] # los adjuntos del mensaje original
            after_attachments = [a.url for a in after.attachments] # los adjuntos del mensaje nuevo 
            removed_attachments = set(before_attachments) - set(after_attachments) # set: para quitar duplicados, ordenar y aplicar operaciones
            added_attachments = set(after_attachments) - set(before_attachments) 

            before_embeds = [str(e.to_dict()) for e in before.embeds] # toma los embeds los convierte en diccionarios (to_dict) y luego en string 
            after_embeds = [str(e.to_dict()) for e in after.embeds]
            removed_embeds = set(before_embeds) - set(after_embeds) # set : listas en conjuntos,  para poder comparar.
            added_embeds = set(after_embeds) - set(before_embeds)

            stickers = [s.name for s in after.stickers] if after.stickers else [] # Si el mensaje tiene stickers (after.stickers), toma el nombre de cada uno (s.name).
            roles = [r.name for r in after.author.roles] if hasattr(after.author, "roles") else [] # hasattr : si el objeto tiene cierto atributo , si el autor posee roles, obtener el nombre del rol
            reactions = after.reactions # guarda las reacciones del mensaje después de la edición.

            embed = Embed(
                title="✏️ ¡Mensaje editado detectado!",
                colour=Colour.orange(),
                timestamp=timestamp
            )
            embed.set_author(name=autor, icon_url=after.author.display_avatar.url)

            embed.add_field(name="👤 Autor", value=autor, inline=True)
            embed.add_field(name="🆔 Autor ID", value=after.author.id, inline=True)
            embed.add_field(name="📍 Canal", value=canal, inline=True)
            embed.add_field(name="🏠 Servidor", value=guild, inline=True)
            embed.add_field(name="🕒 Editado", value=timestamp.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="📄 Antes", value=before.content or "*[Vacío]*", inline=False)
            embed.add_field(name="📄 Después", value=after.content or "*[Vacío]*", inline=False)

            embed.add_field(name="📎 Adjuntos quitados", value="\n".join(removed_attachments) if removed_attachments else "Ninguno", inline=False)
            embed.add_field(name="📎 Adjuntos agregados", value="\n".join(added_attachments) if added_attachments else "Ninguno", inline=False)

            embed.add_field(name="📦 Embeds quitados", value=f"{len(removed_embeds)}" if removed_embeds else "Ninguno", inline=False)
            embed.add_field(name="📦 Embeds agregados", value=f"{len(added_embeds)}" if added_embeds else "Ninguno", inline=False)

            embed.add_field(name="😀 Stickers", value=", ".join(stickers) if stickers else "Ninguno", inline=False)
            embed.add_field(name="🎭 Roles", value=", ".join(roles) if roles else "Ninguno", inline=False) # inline = False ocupará toda la fila del embed
            embed.add_field(name="📊 Reacciones", value=", ".join([str(r) for r in reactions]) if reactions else "Ninguna", inline=False) # ",".join(...): une todos los elementos de esa lista en un solo string, separados por comas.
            embed.add_field(name="🔗 Enlace al mensaje", value=after.jump_url, inline=False) # enlace al mensaje original 

            if isinstance(after.channel, discord.Thread):
                embed.add_field(name="🧵 Hilo", value=after.channel.name, inline=True) # también informa si se está utilizando un hilo

            await after.channel.send(embed=embed)       
        
        @self.bot.event
        async def on_disconnect(): # Este evento se dispara cuando el bot pierde conexión con Discord
            self.logger_chatbot_discord.warning( # es solo para logs internos del chatbot
                f"⚠️ Bot desconectado a las {datetime.now().isoformat()}. " # se documenta inicio de la desconexión 2025-08-17T16:42:51.123456
                f"Guilds activos={len(self.bot.guilds)}, " # se documenta la cantidad de servidores en las que estaba conectado
                f"latencia={getattr(self.bot, 'latency', None)}" # se documenta si había latencia en milisegundos : getattr para obtener del bot el valor del atributo latencia, si es null devuelve None
            )

        @self.bot.event
        async def on_resumed(): # Este evento se dispara cuando el bot logra reconectarse después de una caída
            # es solo para logs internos del bot, pero no para el usuario ya que puede resultar spam o molesto 
            self.logger_chatbot_discord.info(
                f"🔄 Bot reconectado a las {datetime.now().isoformat()}. "
                f"Guilds activos={len(self.bot.guilds)}, "
                f"latencia={getattr(self.bot, 'latency', None)}"
            )
                    
    def run(self):
        self.bot.run(self.token, log_handler=self.discord_handler, log_level=logging.DEBUG)  # ejecuta el bot con el token, guardando logs en el archivo definido



