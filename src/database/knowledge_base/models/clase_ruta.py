from pathlib import Path
import json

class Ruta:
    def __init__(self, nombre_ruta):
        # convertir nombre_ruta en un objeto Path, lo que te permite manipular la ruta de manera más intuitiva.
        self.nombre_ruta = Path(nombre_ruta) 

    def existe(self):
        # Path permite uso de exists: para verificar si la ruta existe
        return self.nombre_ruta.exists()

    def leer_json(self):
        with open(self.nombre_ruta, "r", encoding="utf-8") as f: # abrir el archivo json (nombre_ruta), modo lectura (r) y considerando cacarteres especiales
            return json.load(f) # si el json es clave-valor: load devuelve un diccionario (este caso), si el json es secuencia de valores: devuelve lista

    def __str__(self):
        # definir cómo se representa un objeto cuando se lo convierte en una cadena
        # devolver self.nombre_ruta convertido en una cadena
        return str(self.nombre_ruta)
    # self.nombre_ruta es un objeto Path, la conversión con str(self.nombre_ruta) devuelve la ruta en formato de texto.


'''
Crear una clase para manejar las rutas, porque se van a tener más rutas, se Necesita cargar diferentes carpetas 
según el entorno (local, virtual, etcétera),
y se encapsula lógica como validación de existencia de un archivo.

'''