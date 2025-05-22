import re
# -------------------- FILTRADO DE MENSAJES VACIOS,CON GIF, EMOTICON, GIF, SIMBOLOS CON NUMEROS -----------------------#

# Clase para Filtrado de Contenidos
class FiltradorContenido:
    @staticmethod
    def es_contenido_irrelevante_visual(texto):
        texto = texto.strip().lower()
        solo_emojis = re.fullmatch(r"[\s\U0001F300-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+", texto)
        es_link_tenor_giphy = re.fullmatch(r"(https?:\/\/)?(www\.)?(tenor|giphy)\.com\S*", texto)
        es_sticker_gif = texto in {"sticker", "gif"}
        return bool(solo_emojis or es_link_tenor_giphy or es_sticker_gif)

    @staticmethod
    def es_solo_numeros_signos(texto):
        return bool(re.fullmatch(r"[+\d\s]+", texto))
    
    @staticmethod
    def es_solo_simbolos(texto):
        texto = texto.strip()
        # Si no contiene letras ni números
        return not re.search(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]', texto)
