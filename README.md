# 🤖 Chatbot con IA Generativa para Discord

Este proyecto forma parte de las **Prácticas Profesionales Supervisadas (PPS)** de la carrera **Ingeniería en Sistemas de Información (UTN FRBA)**. Su objetivo es desarrollar un sistema inteligente que permita organizar y recuperar el conocimiento generado en el canal de **Discord** de la materia **Diseño de Sistemas**.

Se basa en el enfoque **RAG (Retrieval-Augmented Generation)**, combinando una **base de datos relacional** con una **base vectorial** para permitir búsquedas semánticas y respuestas contextualizadas con modelos de lenguaje.

---

## 🎯 Objetivo General

Construir un sistema que permita:

1. Filtrar mensajes irrelevantes exportados desde Discord.
2. Detectar preguntas y respuestas en las conversaciones.
3. Almacenar esta información en una base de datos relacional (PostgreSQL).
4. Generar embeddings de preguntas cerradas y almacenarlos en una base de datos vectorial (ChromaDB).
5. Permitir búsquedas semánticas de consultas realizadas por estudiantes.

---

## 🧠 Estado actual del sistema

✔️ **Ya implementado**:

- Carga y limpieza de mensajes exportados desde Discord (`.json`)
- Identificación de preguntas y respuestas utilizando heurísticas
- Persistencia en base relacional (PostgreSQL)
- Generación de embeddings y almacenamiento en ChromaDB
- Búsqueda semántica sobre la base vectorial

🛠️ **En desarrollo**:

- Captura de mensajes de Discord en **tiempo real**
- Clasificación dinámica de mensajes (¿pregunta o respuesta?) con heurísticas o modelos como **Mistral** o **LLaMA**
- Actualización incremental:
  - **Base relacional**: se incorporan nuevos mensajes relevantes
  - **Base vectorial**: se actualiza cuando una pregunta se considera "cerrada"
- Integración del chatbot en un canal específico de Discord (usando la API oficial)
- Orquestación de respuestas con **IA generativa** basada en resultados recuperados

---

## ⚙️ Cómo funciona el sistema

1. **Carga**: Lectura de mensajes desde archivos JSON exportados de Discord y conversión a DataFrame.
2. **Filtrado**: Eliminación de mensajes irrelevantes (solo emojis, stickers, links, etc.).
3. **Clasificación**: Detección de preguntas y respuestas.
4. **Persistencia**:
   - Almacenamiento en base relacional PostgreSQL.
   - Generación y almacenamiento de embeddings de preguntas cerradas en ChromaDB.
5. **Búsqueda semántica**: Una consulta se convierte en un embedding, se busca en la base vectorial y se generan respuestas con un modelo de lenguaje (ej. Mistral).

---

## 📁 Estructura del Proyecto

```
├── chroma/                  # Carpeta donde se guardan los embeddings generados
├── docs/                    # Documentación (diagramas de clases, E-R, flujo del chatbot, etc.)
├── json/                    # Datos exportados desde Discord (.json)
├── logs/                    # Archivos de log con resultados del procesamiento
├── src/                     # Código fuente del sistema
│   ├── database/
│   │   ├── backups/         # Backups de la base
│   │   └── scripts/
│   │       └── inic_tables/ # Scripts de creación de tablas e inserts
│   ├── embeddings/          # Funcionalidad de embeddings y búsqueda semántica
│   ├── utils_for_all/       # Logs y configuración de conexión a la base
│   ├── clasificadores/      # Lógica de detección de preguntas y respuestas
│   ├── filtros/             # Filtros de limpieza de mensajes
│   ├── services/            # Procesamiento de mensajes, análisis y validaciones
│   ├── config/              # Configuración de rutas
│   ├── models/              # Clases del dominio: Pregunta, Respuesta, Mensaje, etc.
│   ├── knowledge_base/
│   │   └── llm_analys/      # Experimentos con LLAMA (no implementado por rendimiento)
│   └── main.py              # Pipeline principal
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Este archivo
```

---

## 🧰 Herramientas y tecnologías

- **Lenguaje**: Python 3.11+
- **Entorno**: Visual Studio Code + venv
- **Bases de datos**: PostgreSQL (relacional) + ChromaDB (vectorial)
- **Librerías principales**:
  - `pandas`, `json`, `re`, `psycopg2`
  - `langchain`, `sentence-transformers`, `chromadb`
  - `python-dotenv`, `logging`, `fastapi`, `scikit-learn`
  - Planeado: `transformers`, `mistral`, `llama` u otros LLMs
- **Integración futura**: API de Discord

---

## 🚀 Cómo ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/LourdesAye/discord-chatbot.git
cd discord-chatbot
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
.env\Scripts\Activate.ps1  # Windows PowerShell
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 4. Configuración de base de datos relacional

Debés tener PostgreSQL instalado. Creá una base de datos con los siguientes parámetros por defecto:

```python
# src/utils_for_all/conexion_bdd.py
"dbname": "base_de_conocimiento_chatbot",
"user": "postgres",
"password": "0909casajardinpaz0707",
"host": "localhost",
"port": "5432"
```

⚠️ Recomendación: Para producción, usar un archivo `.env` para ocultar credenciales.

---

### 4.1 Ejecutar desde cero

1. Eliminar la carpeta `chroma/` (para limpiar embeddings anteriores).
2. Crear la base en PostgreSQL con los datos anteriores.
3. En pgAdmin, ejecutar los siguientes scripts:
   - `src/database/scripts/inic_tables/script_inic_tables.sql`
   - `src/database/scripts/inic_tables/insert_docentes.sql`

### 4.2 Restaurar desde backup `.sql` (opcional)

1. Abrí pgAdmin.
2. Seleccioná la base `base_de_conocimiento_chatbot`.
3. Click derecho > **Restore...** > Seleccioná tu archivo `.sql`.
4. Ejecutá.

---

### 5. Ejecutar el sistema

```bash
python src/main.py
```

Los logs con los resultados se encuentran en la carpeta `logs/`.

---

## ✅ Resultados actuales

- Archivos `.json` son cargados y consolidados en un único DataFrame.
- Se eliminan mensajes irrelevantes y se detectan preguntas/respuestas.
- Se almacena el conocimiento en PostgreSQL.
- Se generan y guardan embeddings en ChromaDB.
- Se permite realizar búsquedas semánticas de forma funcional.

---

## 🔮 Próximos pasos

- Captura de mensajes y clasificación en tiempo real desde Discord.
- Aplicación de modelos como Mistral o LLaMA para clasificación inteligente.
- Actualización automática de bases relacional y vectorial.
- Incorporación de chatbot funcional en Discord.
- Generación de respuestas con IA a partir de los resultados obtenidos.

---

## 👩‍💻 Sobre mí

Proyecto desarrollado por **Lourdes Ayelén González**  
Estudiante de Ingeniería en Sistemas de Información – UTN FRBA  
GitHub: [LourdesAye](https://github.com/LourdesAye)
