-- Script de eliminación (DROP TABLE) en orden correcto
-- BORRADO EN ORDEN INVERSO PARA RESPETAR LAS FK
DROP TABLE IF EXISTS embeddings;
DROP TABLE IF EXISTS fragmentos_preguntas;
DROP TABLE IF EXISTS adjuntos;
DROP TABLE IF EXISTS respuestas;
DROP TABLE IF EXISTS preguntas;
DROP TABLE IF EXISTS mensajes;
DROP TABLE IF EXISTS autores;