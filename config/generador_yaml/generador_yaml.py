from pathlib import Path
import yaml
from src.utils.config_paths import CONFIG_DIR_ABS
from src.utils.utilidades_logs import setup_logger

class GeneradorYAML:
    def __init__(self, diccionario_con_datos_a_convertir_a_yaml,logger_generacion_yaml):
        self.diccionario_con_datos_a_convertir_a_yaml = diccionario_con_datos_a_convertir_a_yaml
        self.logger_generacion_yaml = logger_generacion_yaml

    def generar_yaml(self):
        yaml_dir = CONFIG_DIR_ABS / "yaml"
        try:
            # Crear la carpeta yaml si no existe
            yaml_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"❌ Error al crear carpeta {yaml_dir}: {e}")

        # Guardar cada lista en YAML
        for nombre_lista_a_covertir_a_yaml, lista_a_convertir_a_yaml in self.diccionario_con_datos_a_convertir_a_yaml.items():
            archivo_yaml = yaml_dir / f"{nombre_lista_a_covertir_a_yaml.lower()}.yaml"
            try:
                # crear el archivo YAML o se va a sobreescribir si existe
                with open(archivo_yaml, "w", encoding="utf-8") as f:
                    yaml.dump({nombre_lista_a_covertir_a_yaml: lista_a_convertir_a_yaml}, f, allow_unicode=True)
                self.logger_generacion_yaml.info(f"✅ Guardado: {archivo_yaml}")
            except Exception as e:
                self.logger_generacion_yaml.error(f"❌ Error al guardar {archivo_yaml}: {e}")

    def validar_yaml(self):
        yaml_dir = CONFIG_DIR_ABS / "yaml"

        self.logger_generacion_yaml.info("\n🔎 Validación de archivos YAML:")
        for archivo in yaml_dir.glob("*.yaml"):
            try:
                # Leer el archivo YAML
                with open(archivo, "r", encoding="utf-8") as f:
                    # Cargar el contenido del archivo YAML
                    contenido_arch_yaml = yaml.safe_load(f)
                # Mostrar un resumen: nombre de lista y cantidad de frases
                for nombre_titulo_del_cuerpo_del_arch_yaml, contenido_cuerpo_arch_yaml in contenido_arch_yaml.items():
                    self.logger_generacion_yaml.info(f"📂 Archivo YAML:{archivo.name} → {nombre_titulo_del_cuerpo_del_arch_yaml}: {len(contenido_cuerpo_arch_yaml)} frases")
            except Exception as e:
                self.logger_generacion_yaml.error(f"❌ Error al leer {archivo}: {e}")
