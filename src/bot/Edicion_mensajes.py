import discord
from zoneinfo import ZoneInfo

class MessageDiff:
    def __init__(self, before: discord.Message, after: discord.Message):
        self.before = before
        self.after = after
        self.before_data = self.extract_data(before)
        self.after_data = self.extract_data(after)

    def extract_data(self, msg: discord.Message):
        return {
            "content": msg.content or "*[Vacío]*",
            "attachments": [a.url for a in msg.attachments],
            "embeds": [str(e.to_dict()) for e in msg.embeds],
            "stickers": [s.name for s in msg.stickers] if msg.stickers else [],
            "roles": [r.name for r in getattr(msg.author, "roles", []) if r.name != "@everyone"],
            "reactions": [str(r) for r in msg.reactions],
            "mentions": [m.name for m in msg.mentions],
            "flags": str(msg.flags) if msg.flags else "Ninguna",
            "pinned": "Sí" if msg.pinned else "No",
            "msg_type": msg.type.name,
            "jump_url": msg.jump_url,
            "author": str(msg.author),
            "author_id": msg.author.id,
            "avatar_url": msg.author.display_avatar.url
        }

    def compare_lists(self, key):
        before = self.before_data[key]
        after = self.after_data[key]
        removed = list(set(before) - set(after))
        added = list(set(after) - set(before))
        return removed, added

    def compare_values(self, key):
        return self.before_data[key], self.after_data[key]

    def build_embed(self):
        embed = discord.Embed(
            title="✏️ Edición de Mensaje Detectada",
            colour=discord.Colour.orange(),
            timestamp=self.after.created_at.astimezone(ZoneInfo("America/Argentina/Buenos_Aires"))
        )
        embed.set_thumbnail(url=self.after_data["avatar_url"])

        # 📍 Contexto
        canal = self.after.channel.name
        if isinstance(self.after.channel, discord.Thread):
            embed.add_field(name="🧵 Hilo", value=canal, inline=True)
            embed.add_field(name="📁 Canal padre", value=self.after.channel.parent.name, inline=True)
        else:
            embed.add_field(name="📁 Canal", value=canal, inline=False)

        embed.add_field(name="🏠 Servidor", value=self.after.guild.name if self.after.guild else "DM", inline=False)
        embed.add_field(name="🆔 ID de mensaje", value=str(self.after.id), inline=False)
        embed.add_field(name="👤 Editor", value=self.after_data["author"], inline=True)
        embed.add_field(name="🆔 ID del editor", value=str(self.after_data["author_id"]), inline=True)

        # 📝 Contenido
        embed.add_field(name="📄 Original", value=self.before_data["content"], inline=False)
        embed.add_field(name="📝 Editado", value=self.after_data["content"], inline=False)

        # 📎 Adjuntos
        removed, added = self.compare_lists("attachments")
        embed.add_field(name="📎 Adjuntos quitados", value="\n".join(removed) or "Ninguno", inline=False)
        embed.add_field(name="📎 Adjuntos agregados", value="\n".join(added) or "Ninguno", inline=False)

        # 📋 Embeds
        removed, added = self.compare_lists("embeds")
        embed.add_field(name="📋 Embeds quitados", value=str(len(removed)) or "Ninguno", inline=True)
        embed.add_field(name="📋 Embeds agregados", value=str(len(added)) or "Ninguno", inline=True)

        # 🔍 Listas comparadas
        for key, label in [
            ("mentions", "👥 Menciones"),
            ("roles", "🧑‍💼 Roles"),
            ("stickers", "💟 Stickers"),
            ("reactions", "👍 Reacciones")
        ]:
            removed, added = self.compare_lists(key)
            embed.add_field(name=f"{label} quitadas", value=", ".join(removed) if removed else "Ninguna", inline=False)
            embed.add_field(name=f"{label} agregadas", value=", ".join(added) if added else "Ninguna", inline=False)

        # 🏳️ Valores únicos
        for key, label in [
            ("flags", "🏳️ Banderas"),
            ("pinned", "📌 Anclado"),
            ("msg_type", "✉️ Tipo de mensaje"),
            ("jump_url", "🔗 Enlace")
        ]:
            before, after = self.compare_values(key)
            if before != after:
                embed.add_field(name=f"{label} (antes)", value=before, inline=True)
                embed.add_field(name=f"{label} (después)", value=after, inline=True)

        return embed
