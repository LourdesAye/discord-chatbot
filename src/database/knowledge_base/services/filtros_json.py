import re
# -------------------- FILTRADO DE MENSAJES VACIOS,CON GIF, EMOTICON, GIF, SIMBOLOS CON NUMEROS -----------------------#

# Clase para Filtrado de Contenidos
# class FiltradorContenido:
#     @staticmethod
#     def es_contenido_irrelevante_visual(texto):
#         texto = texto.strip().lower()
#         solo_emojis = re.fullmatch(r"[\s\U0001F300-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+", texto)
#         es_link_tenor_giphy = re.fullmatch(r"(https?:\/\/)?(www\.)?(tenor|giphy)\.com\S*", texto)
#         es_sticker_gif = texto in {"sticker", "gif"}
#         return bool(solo_emojis or es_link_tenor_giphy or es_sticker_gif)

#     @staticmethod
#     def es_solo_numeros_signos(texto):
#         return bool(re.fullmatch(r"[+\d\s]+", texto))
    
#     @staticmethod
#     def es_solo_simbolos(texto):
#         texto = texto.strip()
#         # Si no contiene letras ni números
#         return not re.search(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]', texto)

# Estrategias de filtrado 

# from abc import ABC, abstractmethod
# import re

# class EstrategiaFiltro(ABC):
#     @abstractmethod
#     def aplicar(self, texto: str) -> bool:
#         pass

# class FiltroContenidoVacio(EstrategiaFiltro):
#     def aplicar(self, texto: str) -> bool:
#         texto = texto.strip()
#         return texto == ""

# class FiltroContenidoIrrelevanteVisual(EstrategiaFiltro):
#     def aplicar(self, texto: str) -> bool:
#         texto = texto.strip().lower()
#         solo_emojis = re.fullmatch(r"[\s\U0001F300-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+", texto)
#         es_link_tenor_giphy = re.fullmatch(r"(https?:\/\/)?(www\.)?(tenor|giphy)\.com\S*", texto)
#         es_sticker_gif = texto in {"sticker", "gif"}
#         return bool(solo_emojis or es_link_tenor_giphy or es_sticker_gif)

# class FiltroSoloNumerosSignos(EstrategiaFiltro):
#     def aplicar(self, texto: str) -> bool:
#         return bool(re.fullmatch(r"[+\d\s]+", texto))

# class FiltroSoloSimbolos(EstrategiaFiltro):
#     def aplicar(self, texto: str) -> bool:
#         texto = texto.strip()
#         return not re.search(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]', texto)

from abc import ABC, abstractmethod
#  Interfaz base EstrategiaFiltro
class EstrategiaFiltro(ABC):
    @abstractmethod
    def aplicar(self, texto: str) -> bool:
        pass

    @abstractmethod
    def nombre(self) -> str:
        pass

# Filtros individuales
import re

class FiltroContenidoVacio(EstrategiaFiltro):
    def aplicar(self, texto: str) -> bool:
        return texto.strip() == ""
    def nombre(self) -> str:
        return "vacio"

class FiltroContenidoIrrelevanteVisual(EstrategiaFiltro):
    def aplicar(self, texto: str) -> bool:
        texto = texto.strip().lower()
        solo_emojis = re.fullmatch(r"[\s\U0001F300-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+", texto)
        es_link_tenor_giphy = re.fullmatch(r"(https?:\/\/)?(www\.)?(tenor|giphy)\.com\S*", texto)
        es_sticker_gif = texto in {"sticker", "gif"}
        return bool(solo_emojis or es_link_tenor_giphy or es_sticker_gif)
    def nombre(self) -> str:
        return "irrelevante_visual"

class FiltroSoloNumerosSignos(EstrategiaFiltro):
    def aplicar(self, texto: str) -> bool:
        return bool(re.fullmatch(r"[+\d\s]+", texto))
    def nombre(self) -> str:
        return "solo_numeros_signos"

class FiltroSoloSimbolos(EstrategiaFiltro):
    def aplicar(self, texto: str) -> bool:
        texto = texto.strip()
        return not re.search(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]', texto)
    def nombre(self) -> str:
        return "solo_simbolos"
    

    
