# Módulo para convertir listas largas de cadenas en archivos YAML

## 🎯 Objetivo
El propósito de este módulo es **convertir datos estáticos en archivos YAML estructurados**, facilitando su mantenimiento, reutilización y separación del código fuente.

## 🧱 Estructura del módulo

config  
   ├── datos_a_convertir  
   │   └── datos_a_convertir.py  
   ├── generador_yaml  
   │   └── generador_yaml.py  
   ├── yaml  
   │   ├── docentes.yaml  
   │   ├── archivo_lista_convertida_a_yaml_1.yaml  
   │   ├── archivo_lista_convertida_a_yaml_2.yaml  
   │   ├── ...  
   │   ├── archivo_lista_convertida_a_yaml_N.yaml  
   │   └── generando_yaml.py  
   ├── __init__.py  
   └── README.md  

## 🔄 Evolución del diseño
Se creó la clase `GeneradorYAML`, que automatiza la conversión de listas largas, estáticas y hardcodeadas en archivos YAML, además de validar su correcta creación.  
De esta forma, los datos ya no se mantienen en el código fuente, sino en archivos externos más fáciles de actualizar y versionar.

## 🧩 Estructura actual

- `config/datos_a_convertir/datos_a_convertir.py`: contiene comentarios y ejemplos de cómo se agrupaban las listas originalmente.  
- `config/generador_yaml/generador_yaml.py`: clase que encapsula la lógica de conversión y validación.  
- `config/yaml/`: contiene los archivos `.yaml` generados automáticamente y el script `generando_yaml.py`, con comentarios y ejemplos de cómo ejecutar la conversión mediante la clase `GeneradorYAML`.