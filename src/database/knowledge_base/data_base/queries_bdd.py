query_crear_tablas= """
                    CREATE TABLE IF NOT EXISTS autores ( 
                        id_autor SERIAL PRIMARY KEY,
                        nombre_autor TEXT NOT NULL,
                        es_docente BOOLEAN NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS mensajes (
                        id_mensaje SERIAL PRIMARY KEY,
                        id_mensaje_discord BIGINT NOT NULL,
                        autor_id INTEGER NOT NULL REFERENCES autores(id_autor) ON DELETE CASCADE,
                        fecha_mensaje TIMESTAMP NOT NULL,
                        contenido TEXT NOT NULL,
                        es_pregunta BOOLEAN DEFAULT FALSE,
                        origen TEXT
                    );

                    CREATE TABLE IF NOT EXISTS adjuntos (
                        id_adjunto SERIAL PRIMARY KEY,
                        mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
                        url TEXT NOT NULL,
                        tipo TEXT
                    );

                    CREATE TABLE IF NOT EXISTS preguntas (
                        id_pregunta SERIAL PRIMARY KEY,
                        mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
                        texto TEXT NOT NULL,
                        esta_cerrada BOOLEAN DEFAULT FALSE,
                        sin_contexto BOOLEAN DEFAULT FALSE,
                        es_administrativa BOOLEAN DEFAULT FALSE
                    );

                    CREATE TABLE IF NOT EXISTS respuestas (
                        id_respuesta SERIAL PRIMARY KEY,
                        mensaje_id INTEGER NOT NULL REFERENCES mensajes(id_mensaje) ON DELETE CASCADE,
                        pregunta_id INTEGER NOT NULL REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
                        texto TEXT NOT NULL,
                        orden INTEGER,
                        es_validada BOOLEAN DEFAULT FALSE,
                        es_corta BOOLEAN DEFAULT FALSE
                    );

                    CREATE TABLE IF NOT EXISTS fragmentos_preguntas (
                        id_fragmento SERIAL PRIMARY KEY,
                        pregunta_id INTEGER NOT NULL REFERENCES preguntas(id_pregunta) ON DELETE CASCADE,
                        texto_fragmento TEXT NOT NULL,
                        orden INTEGER NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS embeddings (
                        id_embedding SERIAL PRIMARY KEY,
                        fragmento_id INTEGER NOT NULL REFERENCES fragmentos_preguntas(id_fragmento) ON DELETE CASCADE,
                        id_chroma_db TEXT NOT NULL
                    );
            """

