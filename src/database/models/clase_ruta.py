from pathlib import Path
import json

class Ruta:
    """Wrapper profesional alrededor de pathlib.Path para operaciones específicas del dominio."""

    def __init__(self, nombre_ruta):
        self.nombre_ruta = Path(nombre_ruta)

    def existe(self) -> bool:
        return self.nombre_ruta.exists()

    def leer_json(self):
        """Lee y parsea un archivo JSON de forma segura controlando posibles errores."""
        try:
            with open(self.nombre_ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Error al decodificar el JSON en {self.nombre_ruta}: {e}")
        except IOError as e:
            raise IOError(f"❌ Error de E/S al leer el archivo {self.nombre_ruta}: {e}")

    def __str__(self) -> str:
        return str(self.nombre_ruta)