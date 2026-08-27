import discord
from discord.ext import commands  # permite usar comandos con prefijo (como !ayuda)
from dotenv import load_dotenv  # para cargar variables de entorno desde un archivo .env
import os  # para acceder a variables de entorno del sistema
import logging  # para registrar mensajes en un archivo de log
from utils.utilidades_logs import setup_logger,LOG_DIR_ABS
from datetime import datetime
from discord import Embed, Colour
from zoneinfo import ZoneInfo
from bot.Edicion_mensajes import MessageDiff
from bot.CapturadorMensajes import CapturadorMensajes
from database.models.clase_mensajes import Mensaje
from processing.procesamiento_tiempo_real import ProcesadorTiempoReal
from utils.filtros_de_mensajes import FiltroContenidoIrrelevanteVisual,FiltroSoloNumerosSignos,FiltroSoloSimbolos,FiltroContenidoVacio 
from embeddings.gestor_vectores import GestorBaseVectorial
from langchain_huggingface import HuggingFaceEmbeddings
from psycopg2 import connect, sql, errors
from psycopg2.extras import RealDictCursor, DictCursor
from utils.conexion_bdd import CONFIG

log_real_time = setup_logger('log_real_time', 'log_procesamiento_mensaje_tiempo_real.txt'
                             )
class DiscordChatbot: # encapsula lógica del funcionamiento del chatbot
    def __init__(self):
        # Carga del entorno
        load_dotenv()  # carga las variables del archivo .env al entorno de ejecución

        # Se carga el canal en el que responde o funciona el chatbot
        self.token = os.getenv('DISCORD_TOKEN')  # obtiene el token del bot desde la variable de entorno
        self.nombre_canal_del_chatbot = os.getenv('NOMBRE_CANAL_CHATBOT')  # obtiene el nombre del canal desde .env
        self.id_canal_chatbot = int(os.getenv('ID_CANAL_CHATBOT'))  # obtiene el ID del canal desde .env

        # Carga el o los canales de consulta de los alumnos
        canales_de_consultas = os.getenv("CANALES_DE_CONSULTAS_ALUMNOS") # obtiene el o los nombres de los canales del .env
        ids_de_canales = os.getenv("ID_CANALES_DE_CONSULTAS_ALUMNOS") # obtiene el o los ids de los canales del .env
        # Esto es a mido de inormación temporal, pasar a logs después
        print("Hola! Aquí están los nombres de los canales de consulta:",canales_de_consultas)
        print("Hola! Aquí están los id de los canales de consulta:",ids_de_canales)

        # Si existen los canales de consultas, se convierten en lista
        self.canales_de_consultas = [c.strip() for c in canales_de_consultas.split(",")] if canales_de_consultas else []
        self.ids_canales_de_consultas = [int(i.strip()) for i in ids_de_canales.split(",")] if ids_de_canales else []

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

        # GESTIÓN DE LA BASE VECTORIAL DE EMBEDDINGS
        # configuración del modelo de embeddings y gestor de base vectorial
        modelo = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.gestor_vectorial = GestorBaseVectorial(modelo)

        # intenta cargar/crear base al iniciar
        self.vectordb = self.gestor_vectorial.crear_si_no_existe()

    def obtener_interaccion_completa_pregunta_respuestas(query, id_pregunta):
        conn = connect(**CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)

        cursor.execute(query, (id_pregunta,))

        datos = cursor.fetchall()

        cursor.close()
        conn.close()

        return datos
    
    def formar_mensaje_discord(pregunta, filas):
        mensaje = f"**Pregunta original:**\n> {pregunta}\n\n"
        mensaje += "**Respuestas:**\n"

        for fila in filas:
            etiqueta = "👩‍🏫 Docente" if fila["es_docente"] else "👤 Alumno"
            mensaje += (
                f"\n{etiqueta} — *{fila['nombre_autor']}*\n"
                f"{fila['respuesta']}\n"
                "─" * 20
            )

        return mensaje


    def setup_events(self):
        @self.bot.event
        # mensaje que se da cuando el bot se autentica en discord (cuando comienza a funcionar): No cada vez que se une a un servidor
        async def on_ready(): 
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
        async def on_message(message):
            # Ignora mensajes del propio bot
            if message.author == self.bot.user:
                return

            # --- Datos base del canal ---
            canal = message.channel                # Objeto canal o hilo
            canal_nombre = getattr(canal, "name", "Sin nombre")  # más seguro
            canal_id = getattr(canal, "id", None)  # puede no existir en casos raros

            # --- Caso 1: mensaje en el canal principal del chatbot ---
            # por aquí se deben crear filtros y no crear hilo si no corresponde o genrar hilo indicando que su pegunta no es valida y cerarrlo
            if isinstance(canal, discord.TextChannel) and canal_nombre == self.nombre_canal_del_chatbot:
                self.logger_chatbot_discord.debug(f"📩 Nuevo mensaje en canal principal del chatbot de {message.author}: {message.content}" )
                self.logger_chatbot_discord.debug(f"🔖 Creando hilo para la consulta de {message.author.display_name}...")
                
                mensaje_consulta= message  # alias para mayor claridad
                mention_autor = message.author.mention  # mención del autor para notificarlo en el hilo
                autor = message.author.display_name  # nombre para mensajes

                thread = await canal.create_thread(
                    name=f"Consulta de {autor}",
                    message=mensaje_consulta,
                    auto_archive_duration=60
                )

                # Mensaje informando en el canal principal
                await canal.send(
                    f"📬 Hola {mention_autor}! Creé un hilo para tu consulta. "
                    "Hacé clic en él para continuar nuestra conversación."
                )

                self.logger_chatbot_discord.debug(f"🔖 Hilo creado: {thread.name} (ID: {thread.id})")
                self.logger_chatbot_discord.debug(f"📩 Procesando mensaje de {message.author.display_name} en el hilo...")

                # Mensaje automático dentro del hilo
                await thread.send("🕓 Estoy procesando tu mensaje...")

                if not self.vectordb:
                    await thread.send("Todavía no tengo preguntas cargadas para buscar 😕. Intentalo más tarde")
                    self.logger_chatbot_discord.debug("❌ No existe base de datos relacional para construir base vectorial cargada; se informa al usuario.")
                    return

                texto = message.content or ""
                las_tres_preguntas_mas_parecidas = self.gestor_vectorial.buscar(texto, k=3)

                if not las_tres_preguntas_mas_parecidas:
                    await thread.send("No encontré algo parecido. Podrías preguntar en el canal 🙂")
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

                # Se elige la pregunta más parecida
                resultados_busqueda_semantica, similitud = las_tres_preguntas_mas_parecidas[0]
                pregunta = resultados_busqueda_semantica.page_content
                id_pregunta = resultados_busqueda_semantica.metadata["id"]

                datos = self.obtener_interaccion_completa_pregunta_respuestas(query_respuestas_a_pregunta,id_pregunta)
                mensaje = self.formar_mensaje_discord(pregunta, datos)

                self.logger_chatbot_discord.debug(f"📩 Enviando respuesta al hilo de {autor}...")

                await thread.send(mensaje)

                self.logger_chatbot_discord.debug(f"✅ Respuesta enviada al hilo de {autor}.")

                # Mandar el mensaje de cierre de hilo
                await thread.send(
                    "Tu consulta ya fue respondida 😊\n"
                    "Cerramos el hilo para mantener el canal ordenado.\n"
                    "Si necesitás volver sobre el tema, abrí un hilo nuevo."
                )

                self.logger_chatbot_discord.debug(f"🔖 Cerrando hilo de {autor}...")

                # Archivar y bloquear hilo
                await thread.edit(archived=True, locked=True)
                self.logger_chatbot_discord.debug(f"✅ Hilo de {autor} cerrado y archivado.")
                return  # se evita seguir

            # --- Caso 2: mensaje dentro de un hilo del canal principal ---
            if isinstance(canal, discord.Thread) and canal.parent.name == self.nombre_canal_del_chatbot:

                # Mensaje automático dentro del hilo
                # notar que aquí ya está dentro del hilo, el canal es el hilo
                await  canal.send("🕓 Estoy procesando tu mensaje...")
                mensaje_consulta= message  # alias para mayor claridad
                autor = message.author.display_name  # nombre para mensajes
                self.logger_chatbot_discord.debug(f"📩 Procesando mensaje de {message.author.display_name} en el hilo...")
                # Si aún no existe, crearla (lazy init : si no existe crearla en el momento en que se necesita)

                if not self.vectordb:
                    self.logger_chatbot_discord.debug("Entrando en no existe base vectorial")
                    await canal.send("Todavía no tengo preguntas cargadas para buscar 😕. Intentalo más tarde")
                    self.logger_chatbot_discord.debug("❌ No existe base de datos relacional para construir base vectorial cargada; se informa al usuario.")
                    return
                
                self.logger_chatbot_discord.debug("Entrando en existe base vectorial")
                texto = message.content or ""
                self.logger_chatbot_discord.debug(f"📩 Texto del mensaje a procesar: {texto}")
                self.logger_chatbot_discord.debug("🔎 Iniciando búsqueda semántica...")
                las_tres_preguntas_mas_parecidas = self.gestor_vectorial.buscar(texto, k=3)
                self.logger_chatbot_discord.debug("✅ Búsqueda semántica finalizada")

                if not las_tres_preguntas_mas_parecidas: 
                    self.logger_chatbot_discord.debug("No se encontraron preguntas parecidas") 
                else: 
                    self.logger_chatbot_discord.debug("Se encontraron:", las_tres_preguntas_mas_parecidas)

                if not las_tres_preguntas_mas_parecidas:
                    await canal.send("No encontré algo parecido. Podrías preguntar en el canal 🙂")
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

                # Se elige la pregunta más parecida
                resultados_busqueda_semantica, similitud = las_tres_preguntas_mas_parecidas[0]
                pregunta = resultados_busqueda_semantica.page_content
                id_pregunta = resultados_busqueda_semantica.metadata["id"]

                datos = self.obtener_interaccion_completa_pregunta_respuestas(query_respuestas_a_pregunta,id_pregunta)
                mensaje_para_discord = self.formar_mensaje_discord(pregunta, datos)

                self.logger_chatbot_discord.debug(f"📩 Enviando respuesta al hilo de {autor}...")

                await canal.send(mensaje_para_discord)

                self.logger_chatbot_discord.debug(f"✅ Respuesta enviada al hilo de {autor}.")

                # Mandar el mensaje de cierre de hilo
                await thread.send(
                    "Tu consulta ya fue respondida 😊\n"
                    "Cerramos el hilo para mantener el canal ordenado.\n"
                    "Si necesitás volver sobre el tema, abrí un hilo nuevo."
                )

                self.logger_chatbot_discord.debug(f"🔖 Cerrando hilo de {autor}...")

                # Archivar y bloquear hilo
                await canal.edit(archived=True, locked=True)
                self.logger_chatbot_discord.debug(f"✅ Hilo de {autor} cerrado y archivado.")
                return  # se evita seguir

            # --- Caso 3: mensaje en un canal de consulta ---
            # (por nombre o por ID)
            # 🔸 Convertimos todo a string para evitar comparaciones tipo int vs str
            canales_validos = set(str(c) for c in self.canales_de_consultas)
            ids_validos = set(str(i) for i in self.ids_canales_de_consultas)

            if str(canal_nombre) in canales_validos or str(canal_id) in ids_validos:
                # Obtener el texto del mensaje
                texto_mensaje = message.content or ""  
                # Generar los filtros para determinar si el mensaje se analizará o no
                estrategias_filtro_mensaje =[ FiltroContenidoVacio(),FiltroContenidoIrrelevanteVisual(), FiltroSoloNumerosSignos(),FiltroSoloSimbolos()]
                for estrategia_de_filtro in estrategias_filtro_mensaje: 
                    nombre_filtro = estrategia_de_filtro.nombre() # se capta nombre de la estrategia
                    es_aceptable_mensaje = estrategia_de_filtro.aplicar(texto_mensaje) # se aplica el filtro en el mensaje
                    if es_aceptable_mensaje: # si el mensaje es filtrado (no es aceptable)
                        self.logger_chatbot_discord.debug(f"❌ Mensaje filtrado por '{nombre_filtro}': {texto_mensaje}") # para trazabilidad de mensajes filtrados de acuerdo a la estrategia
                        await canal.send(f"⚠️ Tu mensaje fue filtrado por el criterio '{nombre_filtro}' y no será procesado. Por favor, envía un mensaje válido.")
                        return # se termina el proceso del mensaje
                # Si pasa todos los filtros, se procesa el mensaje
                await canal.send("Tu mensaje ha sido recibido y está siendo procesado...")
                mensaje = Mensaje.from_discord(message)  # procesa el mensaje recibido desde Discord
                procesador_real_time = ProcesadorTiempoReal(log_real_time)
                procesador_real_time.procesar_mensaje(mensaje)  # procesa el mensaje usando el procesador de tiempo real
                attachments = []
                try: # algunos mensajes pueden no tener attachments
                    for a in message.attachments: 
                        # ejemplo de attachments:
                            #  [<Attachment 
                            # id=1426312557093978203 
                            # filename='refelxion_uso_de_herrameintas_en_tic_y_general.docx' 
                            # url='refelxion_uso_de_herrameintas_en_tic_y_general.docx'>, 
                            # <Attachment 
                            # id=1426312557450498140 
                            # filename='Charlas_empleab_ilidad_utn_frba_2_oct.docx' 
                            # url='Charlas_empleab_ilidad_utn_frba_2_oct.docx'>]
                        filename = getattr(a, "filename", str(a))
                            # ejemplo de filename: Charlas_empleab_ilidad_utn_frba_2_oct.docx
                        ext = filename.split('.')[-1] if '.' in filename else ''
                            # "Mi nombre es Lourdes".split(' ') -> ['Mi', 'nombre', 'es', 'Lourdes']
                            # ejemplo de ext: docx
                        attachments.append((filename, ext)) # agrega una tupla (nombre,extensión) a la lista
                    
                    # aca recibo mensaje: debo tomar texto y adjuntos
                    # debo enviar a procesar al mensaje
                    # hay que crear un procesador y que se encargue de ello
                    return
                except Exception:
                # si no tiene attachments o estructura diferente, dejamos lista vacía
                    attachments = []
                    return

            # --- Caso 4: mensaje en cualquier otro canal ---
            content = message.content or "*[Vacío]*"
            author = str(message.author)
            guild = message.guild.name if message.guild else "DM"
            msg_id = message.id

            # Hora local (Argentina)
            local_time = message.created_at.astimezone(ZoneInfo("America/Argentina/Buenos_Aires"))
            timestamp = local_time.strftime("%Y-%m-%d %H:%M:%S")

            # Adjuntos, menciones, etc.
            attachments = [a.url for a in message.attachments]
            embeds = message.embeds
            mentions = [m.name for m in message.mentions]
            reactions = [str(r) for r in message.reactions]
            flags = message.flags
            pinned = message.pinned
            msg_type = message.type.name
            edited = message.edited_at.strftime("%Y-%m-%d %H:%M:%S") if message.edited_at else "Sin editar"
            stickers = [s.name for s in message.stickers] if message.stickers else []

            # Roles (si el autor los tiene)
            roles = []
            if hasattr(message.author, "roles"):
                roles = [r.name for r in message.author.roles if r.name != "@everyone"]

            # Enlace directo
            jump = message.jump_url

            # --- Construcción del Embed ---
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

            # --- Procesar comandos (si existen) ---
            await self.bot.process_commands(message)
                    
        @self.bot.event
        async def on_message_edit(self,before_message: discord.Message, after_message: discord.Message): # Evento: cuando un mensaje es editado
            
            if after_message.author == self.bot.user: # no se responde a sí mismo
                return

            diff = MessageDiff(before_message, after_message)
            embed = diff.build_embed()
            await after_message.channel.send(embed=embed)       
        
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

    def hay_canal_de_consulta():
        return True# aca van las validaciones de las dos listas nombre_canal_consulta y los ids_canales_consulta

# tengo una carpeta llamada utils_for_all que tiene un archivo llamado
# conexion_bdd.py y tiene este contenido: 
# from dotenv import load_dotenv
# import os
# from utils_for_all.utilidades_logs import setup_logger

# # Inicializar logger para esta parte del sistema
# logger_db= setup_logger('carga_db','log_persistencia_de_datos.txt')

# # Cargar variables desde .env
# load_dotenv()

# # Obtener configuración desde variables de entorno (.env)
# config = {
#     "dbname": os.getenv("DB_NAME"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "host": os.getenv("DB_HOST"),
#     "port": os.getenv("DB_PORT")
# }

# # Validación con log
# if not all(config.values()):
#     logger_db.error("❌ Faltan variables de entorno para la conexión a la base de datos. Verificá el archivo .env.")
#     raise ValueError("Faltan datos de conexión a la base de datos. Verificá el archivo .env")
# else:
#     logger_db.info("✅ Variables de entorno cargadas correctamente para la conexión a la base de datos.")


# Por otro lado la estructura de la base de datos relacional es:
# CREATE TABLE autores (
#     id_autor SERIAL PRIMARY KEY,
#     nombre_autor TEXT NOT NULL,
#     es_docente BOOLEAN NOT NULL
# );

# CREATE TABLE mensajes (
#     id_mensaje SERIAL PRIMARY KEY,
#     id_mensaje_discord BIGINT NOT NULL,
#     autor_id INTEGER NOT NULL REFERENCES autores(id_autor) ON DELETE CASCADE,
#     fecha_mensaje TIMESTAMP NOT NULL,
#     contenido TEXT NOT NULL,
#     es_pregunta BOOLEAN DEFAULT FALSE,
#     origen TEXT
# );

# CREATE TABLE adjuntos (
#     id_adjunto SERIAL PRIMARY KEY,
#     mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
#     url TEXT NOT NULL,
#     tipo TEXT
# );

# CREATE TABLE preguntas (
#     id_pregunta SERIAL PRIMARY KEY,
#     mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
#     texto TEXT NOT NULL,
#     esta_cerrada BOOLEAN DEFAULT FALSE,
#     sin_contexto BOOLEAN DEFAULT FALSE,
#     es_administrativa BOOLEAN DEFAULT FALSE
# );

# CREATE TABLE respuestas (
#     id_respuesta SERIAL PRIMARY KEY,
#     mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
#     pregunta_id INTEGER NOT NULL REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
#     texto TEXT NOT NULL,
#     orden INTEGER,
#     es_validada BOOLEAN DEFAULT FALSE,
#     es_corta BOOLEAN DEFAULT FALSE
# );

# CREATE TABLE fragmentos_preguntas (
#     id_fragmento SERIAL PRIMARY KEY,
#     pregunta_id INTEGER NOT NULL REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
#     texto_fragmento TEXT NOT NULL,
#     orden INTEGER NOT NULL
# );

# CREATE TABLE embeddings (
#     id_embedding SERIAL PRIMARY KEY,
#     fragmento_id INTEGER NOT NULL REFERENCES fragmentos_preguntas(id_fragmento) ON DELETE CASCADE,
#     id_chroma_db TEXT NOT NULL
# );

