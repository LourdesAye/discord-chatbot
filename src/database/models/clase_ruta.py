# wrapper (envoltorio) alrededor de pathlib.Path que añade funcionalidad específica para tu proyecto 
# (como leer JSONs y verificar existencia).

from pathlib import Path
import json

class Ruta:
    def __init__(self, nombre_ruta):
        self.nombre_ruta = Path(nombre_ruta) # Convierte string/Path a objeto Path

    def existe(self):
        return self.nombre_ruta.exists() # True si la ruta existe en el filesystem

    def leer_json(self):
        with open(self.nombre_ruta, "r", encoding="utf-8") as f: # abrir el archivo json (nombre_ruta), modo lectura (r) y considerando cacarteres especiales
            return json.load(f) # si el json es clave-valor: load devuelve un diccionario (este caso), si el json es secuencia de valores: devuelve lista

    def __str__(self):
        # definir cómo se representa un objeto cuando se lo convierte en una cadena
        # devolver self.nombre_ruta convertido en una cadena
        return str(self.nombre_ruta)
    # self.nombre_ruta es un objeto Path, la conversión con str(self.nombre_ruta) devuelve la ruta en formato de texto.
