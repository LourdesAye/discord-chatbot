# código o funciones que lo usás en cualquier parte
# se llama o invoca: 
    # Misma carpeta: from utilidades import algo
    # Otra carpeta: from carpeta.utilidades import algo

import json
import pandas as pd
import re
import os
from datetime import datetime, timedelta


# Eliminar mensajes que sean solo emojis, solo stickers, gifs o enlaces tipo tenor/giphy
def es_contenido_irrelevante_visual(texto):
    texto = texto.strip().lower()
    # Si es solo emojis (todos los caracteres son emojis o espacios)
    solo_emojis = re.fullmatch(r"[\s\U0001F300-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+", texto)
    # Si contiene solo un link tipo Tenor o Giphy
    es_link_tenor_giphy = re.fullmatch(r"(https?:\/\/)?(www\.)?(tenor|giphy)\.com\S*", texto)
    # Si solo dice "sticker" o "gif"
    es_sticker_gif = texto in {"sticker", "gif"}

    return bool(solo_emojis or es_link_tenor_giphy or es_sticker_gif)

# eliminar solo numeros o combinacion de numero mas signo como +1
def es_solo_numeros_signos(texto):
    return bool(re.fullmatch(r"[+\d\s]+", texto))