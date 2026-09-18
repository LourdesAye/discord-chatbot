import yaml
from pathlib import Path
from src.utils.utilidades_logs import setup_logger
from src.utils.config_paths import CONFIG_DIR_ABS
from src.database.models.clase_ruta import Ruta

logger_cargador_yaml = setup_logger("logger_cargador_yaml", "cargador_yaml.log")

from typing import Any, Union, Dict, List

class GestorYAML:

    def __init__(self):
        pass

    def cargar_datos_yaml(nombre_yaml: str, clave_especifica: str = None) -> Union[Dict[str, List[Any]], List[Any]]:
        """
        Carga un archivo YAML desde `config/yaml`, valida su estructura de listas y permite extraer una clave ("título") específica si se requiere.
        """
        yaml_path = Ruta(CONFIG_DIR_ABS / "yaml" / nombre_yaml)

        try:
            if not yaml_path.existe():
                raise FileNotFoundError(f"Archivo no encontrado: {yaml_path}")

            with open(yaml_path.nombre_ruta, "r", encoding="utf-8") as f:
                contenido_del_yaml = yaml.safe_load(f)

            # Validación si el YAML está vacío o se carga como un diccionario
            if not isinstance(contenido_del_yaml, dict):
                raise ValueError(f"El archivo {nombre_yaml} esta vacío o no tiene la estructura requerida")

            # se analiza que cada sección del YAML sean listas válidas
            for clave, lista in contenido_del_yaml.items():
                if isinstance(lista, list):
                    logger_cargador_yaml.info(
                        f"✅ {len(lista)} elementos en la sección '{clave}'"
                    )
                else:
                    logger_cargador_yaml.error(
                        f"❌ El contenido de '{clave}' no es una lista en {nombre_yaml}"
                    )
                    raise ValueError(f"El contenido de '{clave}' no es una lista.")

            # Para un título o sección específica
            if clave_especifica is not None:
                if clave_especifica in contenido_del_yaml:
                    return contenido_del_yaml[clave_especifica]
                else:
                    # Si se pide algo que no existe, se lanza un error controlado
                    logger_cargador_yaml.error(f"❌ La clave '{clave_especifica}' no existe en {nombre_yaml}")
                    raise KeyError(f"La clave '{clave_especifica}' no fue encontrada en el archivo.")

            # Si no se puso una clave, se devuelve el diccionario
            return contenido_del_yaml

        except Exception as e:
            logger_cargador_yaml.error(f"❌ Error al procesar {nombre_yaml}: {e}")
            raise RuntimeError(f"Error al procesar {nombre_yaml}: {e}")

