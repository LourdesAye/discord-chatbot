# -------------------- FILTRADO DE MENSAJES VACIOS,CON GIF, EMOTICON, GIF, SIMBOLOS CON NUMEROS (usando patrón de diseño Strategy)-----------------------#

# abc (en minúscula) es un módulo de Python que proporciona herramientas para crear clases abstractas.
# ABC (en mayúscula) es una clase dentro de ese módulo que usamos como base para definir nuestras propias clases abstractas.
# ABC: "Abstract Base Class" es una clase abstracta (que en este caso simula ser una interface)
# es una plantilla que no se puede instanciar directamente, sirve para que otras clases herenden de ella y obliga a implementar métodos
# Si intentas crear un objeto de EstrategiaFiltro directamente, Python dará error.
# Las clases hijas deben implementar aplicar() y nombre(), o también darán error.

import re
from abc import ABC, abstractmethod  # Del módulo `abc`, se importa la clase `ABC` y el decorador `abstractmethod`
class EstrategiaFiltro(ABC): # Hereda de ABC para ser una clase abstracta (que en este caso simula ser una interface) (es un contrato)
    
    @abstractmethod # para marcar métodos que deben ser implementados obligatoriamente por las clases hijas.
    def aplicar(self, texto: str) -> bool: # Los métodos abstractos no tienen implementación (solo firma).
        pass # Esto obliga a que las clases hijas implementen este método

    @abstractmethod # para marcar métodos que deben ser implementados obligatoriamente por las clases hijas.
    def nombre(self) -> str: # Los métodos abstractos no tienen implementación (solo firma).
        pass # Esto obliga a que las clases hijas implementen este método

# Filtros individuales: clases hijas de la clase abstracta EstrategiaFiltro
# Todas siguen correctamente el contrato de EstrategiaFiltro: Implementa ambos métodos abstractos.
# Todas las clases hijas pueden usarse de manera intercambiable (polimorfismo).
# se pueden añadir nuevos filtros sin modificar el código existente (extensibilidad).
# se deben implementar los métodos abstractos para evitanr errores (control).

class FiltroContenidoVacio(EstrategiaFiltro): # la clase FiltroContenidoVacio hereda de EstrategiaFiltro
   
    def aplicar(self, texto: str) -> bool: # Implementa el método abstracto
        return texto.strip() == ""
    
    def nombre(self) -> str: # Implementa el método abstracto
        return "vacio"

class FiltroContenidoIrrelevanteVisual(EstrategiaFiltro): # la clase FiltroContenidoIrrelevanteVisual  hereda de EstrategiaFiltro
    
    def aplicar(self, texto: str) -> bool: # Implementa el método abstracto
        texto = texto.strip().lower()
        solo_emojis = re.fullmatch(r"[\s\U0001F300-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF]+", texto)
        es_link_tenor_giphy = re.fullmatch(r"(https?:\/\/)?(www\.)?(tenor|giphy)\.com\S*", texto)
        es_sticker_gif = texto in {"sticker", "gif"}
        return bool(solo_emojis or es_link_tenor_giphy or es_sticker_gif)
   
    def nombre(self) -> str: # Implementa el método abstracto
        return "irrelevante_visual"

class FiltroSoloNumerosSignos(EstrategiaFiltro): # la clase FiltroSoloNumerosSignos hereda de EstrategiaFiltro
   
    def aplicar(self, texto: str) -> bool: # Implementa el método abstracto
        return bool(re.fullmatch(r"[+\d\s]+", texto))
    
    def nombre(self) -> str: # Implementa el método abstracto
        return "solo_numeros_signos"

class FiltroSoloSimbolos(EstrategiaFiltro): # la clase  FiltroSoloSimbolos hereda de EstrategiaFiltro
   
    def aplicar(self, texto: str) -> bool: # Implementa el método abstracto
        texto = texto.strip()
        return not re.search(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]', texto)
   
    def nombre(self) -> str: # Implementa el método abstracto
        return "solo_simbolos"
    

    
