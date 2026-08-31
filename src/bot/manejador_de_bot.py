import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands
from discord import Embed, Colour
from dotenv import load_dotenv

from utils.utilidades_logs import setup_logger
from bot.Edicion_mensajes import MessageDiff
from database.models.clase_mensajes import Mensaje
from processing.procesamiento_tiempo_real import ProcesadorTiempoReal
from utils.filtros_de_mensajes import (
    FiltroContenidoIrrelevanteVisual,
    FiltroSoloNumerosSignos,
    FiltroSoloSimbolos,
    FiltroContenidoVacio
)
from embeddings.gestor_vectores import GestorBaseVectorial
from langchain_huggingface import HuggingFaceEmbeddings
from psycopg2 import connect
from psycopg2.extras import DictCursor
from utils.conexion_bdd import CONFIG

log_real_time = setup_logger('log_real_time', 'log_procesamiento_mensaje_tiempo_real.txt')

class DiscordChatbot:
    """Encapsula la lógica del funcionamiento del chatbot en Discord."""
    
    def __init__(self):
        load_dotenv()
        
        self.token = os.getenv('DISCORD_TOKEN')
        self.nombre_canal_del_chatbot = os.getenv('NOMBRE_CANAL_CHATBOT')
        self.id_canal_chatbot = int(os.getenv('ID_CANAL_CHATBOT'))
        
        canales_de_consultas = os.getenv("CANALES_DE_CONSULTAS_ALUMNOS")
        ids_de_canales = os.getenv("ID_CANALES_DE_CONSULTAS_ALUMNOS")
        
        self.canales_de_consultas = [c.strip() for c in canales_de_consultas.split(",")] if canales_de_consultas else []
        self.ids_canales_de_consultas = [int(i.strip()) for i in ids_de_canales.split(",")] if ids_de_canales else []
        
        fecha_discord_log = datetime.now().strftime("log_discord_%d_%m_%y_%H_%M")
        archivo_log_discord = os.path.join(LOG_DIR_ABS, fecha_discord_log)
        self.discord_handler = logging.FileHandler(filename=archivo_log_discord, encoding='utf-8', mode='w')
        
        self.logger_chatbot_discord = setup_logger('chatbot_con_discord', 'log_chatbot_integracion_discord.txt')
        
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        
        self.bot = commands.Bot(command_prefix="", intents=intents)
        self.setup_events()
        
        modelo = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.gestor_vectorial = GestorBaseVectorial(modelo)
        self.vectordb = self.gestor_vectorial.crear_si_no_existe()

    def obtener_interaccion_completa_pregunta_respuestas(self, query, id_pregunta):
        conn = connect(**CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(query, (id_pregunta,))
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos

    def formar_mensaje_discord(self, pregunta, filas):
        mensaje = f"**Pregunta original:**\n>{pregunta}\n\n"
        mensaje += "**Respuestas:**\n"
        for fila in filas:
            etiqueta = "👩‍🏫 Docente" if fila["es_docente"] else "👤 Alumno"
            mensaje += (
                f"\n{etiqueta} — *{fila['nombre_autor']}*\n"
                f"{fila['respuesta']}\n"
                f"{"─"*20}"
            )
        return mensaje

    async def _procesar_y_responder_consulta(self, destino, mensaje_texto, autor_nombre):
        """Método auxiliar unificado para realizar la búsqueda semántica y responder en un canal o hilo."""
        await destino.send("🕓 Estoy procesando tu mensaje...")

        if not self.vectordb:
            await destino.send("Todavía no tengo preguntas cargadas para buscar 😕. Intentalo más tarde")
            self.logger_chatbot_discord.debug("❌ No existe base vectorial cargada; se informa al usuario.")
            return

        las_tres_preguntas_mas_parecidas = self.gestor_vectorial.buscar(mensaje_texto, k=3)

        if not las_tres_preguntas_mas_parecidas:
            await destino.send("No encontré algo parecido. Podrías preguntar en el canal 🙂")
            self.logger_chatbot_discord.debug("❌ No se encontraron preguntas parecidas; se informa al usuario.")
            return

        query_respuestas_a_pregunta = """
            SELECT 
                p.texto AS pregunta,
                r.texto AS respuesta,
                r.orden,
                r.es_validada,
                a.nombre_autor,
                a.es_docente
            FROM preguntas p
            JOIN respuestas r ON r.pregunta_id = p.id_pregunta
            JOIN mensajes m ON m.id_mensaje = r.mensaje_id
            JOIN autores a ON a.id_autor = m.autor_id
            WHERE p.id_pregunta = %s
            ORDER BY r.orden NULLS LAST, r.id_respuesta;
        """

        resultados_busqueda_semantica, similitud = las_tres_preguntas_mas_parecidas[0]
        pregunta = resultados_busqueda_semantica.page_content
        id_pregunta = resultados_busqueda_semantica.metadata["id"]

        datos = self.obtener_interaccion_completa_pregunta_respuestas(query_respuestas_a_pregunta, id_pregunta)
        mensaje_para_discord = self.formar_mensaje_discord(pregunta, datos)

        self.logger_chatbot_discord.debug(f"📩 Enviando respuesta al hilo de {autor_nombre}...")
        await destino.send(mensaje_para_discord)
        self.logger_chatbot_discord.debug(f"✅ Respuesta enviada al hilo de {autor_nombre}.")

        # Cierre y archivo del hilo si el destino es un Thread
        if isinstance(destino, discord.Thread):
            await destino.send(
                "Tu consulta ya fue respondida 😊\n"
                "Cerramos el hilo para mantener el canal ordenado.\n"
                "Si necesitás volver sobre el tema, abrí un hilo nuevo."
            )
            self.logger_chatbot_discord.debug(f"🔖 Cerrando hilo de {autor_nombre}...")
            await destino.edit(archived=True, locked=True)
            self.logger_chatbot_discord.debug(f"✅ Hilo de {autor_nombre} cerrado y archivado.")

    def setup_events(self):
        @self.bot.event
        async def on_ready():
            self.logger_chatbot_discord.debug(f"✅ Bot conectado como {self.bot.user}")
            for guild in self.bot.guilds:
                canal = None
                if self.id_canal_chatbot:
                    canal = self.bot.get_channel(int(self.id_canal_chatbot))
                if not canal and self.nombre_canal_del_chatbot:
                    canal = discord.utils.get(guild.text_channels, name=self.nombre_canal_del_chatbot)
                if canal:
                    await canal.send(f"🤖 ¡Bot conectado como {self.bot.user}!")
                    self.logger_chatbot_discord.debug(f"✅ Mensaje de autenticación exitosa enviado al canal #{canal.name} en {guild.name}")
                else:
                    self.logger_chatbot_discord.debug(f"❌ Canal no encontrado en el servidor: {guild.name}")

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return

            canal = message.channel
            canal_nombre = getattr(canal, "name", "Sin nombre")
            canal_id = getattr(canal, "id", None)

            # --- Caso 1: mensaje en el canal principal del chatbot ---
            if isinstance(canal, discord.TextChannel) and canal_nombre == self.nombre_canal_del_chatbot:
                self.logger_chatbot_discord.debug(f"📩 Nuevo mensaje en canal principal del chatbot de {message.author}: {message.content}")
                self.logger_chatbot_discord.debug(f"🔖 Creando hilo para la consulta de {message.author.display_name}...")
                
                autor = message.author.display_name
                mention_autor = message.author.mention

                thread = await canal.create_thread(
                    name=f"Consulta de {autor}",
                    message=message,
                    auto_archive_duration=60
                )

                await canal.send(
                    f"📬 Hola {mention_autor}! Creé un hilo para tu consulta. "
                    "Hacé clic en él para continuar nuestra conversación."
                )
                
                texto = message.content or ""
                await self._procesar_y_responder_consulta(thread, texto, autor)
                return

            # --- Caso 2: mensaje dentro de un hilo del canal principal ---
            if isinstance(canal, discord.Thread) and canal.parent.name == self.nombre_canal_del_chatbot:
                autor = message.author.display_name
                texto = message.content or ""
                await self._procesar_y_responder_consulta(canal, texto, autor)
                return

            # --- Caso 3: mensaje en un canal de consulta ---
            canales_validos = set(str(c) for c in self.canales_de_consultas)
            ids_validos = set(str(i) for i in self.ids_canales_de_consultas)

            if str(canal_nombre) in canales_validos or str(canal_id) in ids_validos:
                texto_mensaje = message.content or ""
                estrategias_filtro_mensaje = [
                    FiltroContenidoVacio(),
                    FiltroContenidoIrrelevanteVisual(),
                    FiltroSoloNumerosSignos(),
                    FiltroSoloSimbolos()
                ]
                
                for estrategia_de_filtro in estrategias_filtro_mensaje:
                    nombre_filtro = estrategia_de_filtro.nombre()
                    es_aceptable_mensaje = estrategia_de_filtro.aplicar(texto_mensaje)
                    if es_aceptable_mensaje:
                        self.logger_chatbot_discord.debug(f"❌ Mensaje filtrado por '{nombre_filtro}': {texto_mensaje}")
                        await canal.send(f"⚠️ Tu mensaje fue filtrado por el criterio '{nombre_filtro}' y no será procesado. Por favor, envía un mensaje válido.")
                        return

                await canal.send("Tu mensaje ha sido recibido y está siendo procesado...")
                mensaje_obj = Mensaje.from_discord(message)
                procesador_real_time = ProcesadorTiempoReal(log_real_time)
                procesador_real_time.procesar_mensaje(mensaje_obj)
                return

            # --- Caso 4: mensaje en cualquier otro canal ---
            content = message.content or "*[Vacío]*"
            author = str(message.author)
            guild = message.guild.name if message.guild else "DM"
            msg_id = message.id
            
            local_time = message.created_at.astimezone(ZoneInfo("America/Argentina/Buenos_Aires"))
            timestamp = local_time.strftime("%Y-%m-%d %H:%M:%S")

            attachments = [a.url for a in message.attachments]
            embeds = message.embeds
            mentions = [m.name for m in message.mentions]
            reactions = [str(r) for r in message.reactions]
            flags = message.flags
            pinned = message.pinned
            msg_type = message.type.name
            edited = message.edited_at.strftime("%Y-%m-%d %H:%M:%S") if message.edited_at else "Sin editar"
            stickers = [s.name for s in message.stickers] if message.stickers else []

            roles = []
            if hasattr(message.author, "roles"):
                roles = [r.name for r in message.author.roles if r.name != "@everyone"]

            jump = message.jump_url

            embed = Embed(
                title="📩 Nuevo Mensaje Registrado",
                colour=Colour.green(),
                timestamp=message.created_at
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.add_field(name="👤 Autor del mensaje registrado:", value=author, inline=False)
            embed.add_field(name="🆔 ID de autor:", value=message.author.id, inline=False)

            if isinstance(message.channel, discord.Thread):
                embed.add_field(name="#️⃣ Canal principal:", value=canal.parent.name, inline=False)
                embed.add_field(name="🧵 Hilo:", value=canal.name, inline=True)
            else:
                embed.add_field(name="#️⃣ Canal:", value=canal_nombre, inline=False)

            embed.add_field(name="🗄️ Servidor:", value=guild, inline=False)
            embed.add_field(name="🆔 ID del mensaje:", value=msg_id, inline=False)
            embed.add_field(name="🕐 Fecha y hora:", value=timestamp, inline=False)
            embed.add_field(name="📝 Editado:", value=edited, inline=False)
            embed.add_field(name="💬 Contenido:", value=content, inline=False)
            embed.add_field(name="📎 Archivos:", value="\n".join(attachments) if attachments else "Ninguno", inline=False)
            embed.add_field(name="📋 Embeds:", value=f"{len(embeds)} encontrados" if embeds else "Ninguno", inline=False)
            embed.add_field(name="👥 Menciones:", value=", ".join(mentions) if mentions else "Ninguna", inline=False)
            embed.add_field(name="🧑‍💼 Roles:", value=", ".join(roles) if roles else "Ninguno", inline=False)
            embed.add_field(name="💟 Stickers:", value=", ".join(stickers) if stickers else "Ninguno", inline=False)
            embed.add_field(name="👍 Reacciones:", value=", ".join(reactions) if reactions else "Ninguna", inline=False)
            embed.add_field(name="🏳️ Banderas:", value=str(flags) if flags else "Ninguna", inline=False)
            embed.add_field(name="📌 Fijado:", value="Sí" if pinned else "No", inline=False)
            embed.add_field(name="✉️ Tipo de mensaje:", value=msg_type, inline=False)
            embed.add_field(name="🔗 Enlace:", value=jump, inline=False)

            await message.channel.send(embed=embed)
            await self.bot.process_commands(message)

        @self.bot.event
        async def on_message_edit(before_message: discord.Message, after_message: discord.Message):
            if after_message.author == self.bot.user:
                return

            diff = MessageDiff(before_message, after_message)
            embed = diff.build_embed()
            await after_message.channel.send(embed=embed)
        
        @self.bot.event
        async def on_disconnect():
            self.logger_chatbot_discord.warning(
                f"⚠️ Bot desconectado a las {datetime.now().isoformat()}. "
                f"Guilds activos={len(self.bot.guilds)}, "
                f"latencia={getattr(self.bot, 'latency', None)}"
            )

        @self.bot.event
        async def on_resumed():
            self.logger_chatbot_discord.info(
                f"🔄 Bot reconectado a las {datetime.now().isoformat()}. "
                f"Guilds activos={len(self.bot.guilds)}, "
                f"latencia={getattr(self.bot, 'latency', None)}"
            )

    def run(self):
        self.bot.run(self.token, log_handler=self.discord_handler, log_level=logging.DEBUG)