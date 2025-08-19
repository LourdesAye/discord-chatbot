import discord
from discord.ext import commands
import pandas as pd

class CapturadorMensajes:
    def __init__(self, nombre_canal):
        self.nombre_canal = nombre_canal
        self.df_mensajes = pd.DataFrame(columns=["id", "author", "content", "timestamp", "attachments"])

    async def procesar_mensaje(self, message):
        # Ignorar mensajes del propio bot
        if message.author == message.guild.me:
            return

        canal = message.channel

        # Solo procesar mensajes del canal que nos interesa
        if isinstance(canal, discord.TextChannel) and canal.name == self.nombre_canal:
            attachments = [(a.filename, a.content_type) for a in message.attachments]

            mensaje_info = {
                "id": message.id,
                "author": message.author.name,
                "content": message.content,
                "timestamp": message.created_at,
                "attachments": attachments
            }

            # Agregar al DataFrame
            self.df_mensajes = pd.concat([self.df_mensajes, pd.DataFrame([mensaje_info])], ignore_index=True)

            # Mostrar por pantalla en Discord
            await canal.send(f"Capté esto: {mensaje_info}")

    def obtener_dataframe(self):
        # Devuelve el DataFrame actual
        return self.df_mensajes

