"""
MAIN BOT — Proceso en tiempo real que mantiene vivo al chatbot de Discord.

Este archivo se ejecuta cuando quiero levantar el bot para que escuche mensajes
de los canales de Discord y responda consultas usando la base de conocimiento
ya construida previamente (por el main_offline).

¿Qué hace este proceso?
1. Conecta el bot al servidor y a los canales de Discord.
2. Escucha mensajes nuevos (on_message).
3. Detecta si un mensaje es pregunta o respuesta.
4. Actualiza la base relacional y la base vectorial en tiempo real.
5. Realiza búsquedas semánticas para responder a los alumnos.
6. Crea hilos, responde, valida, y mantiene el flujo de interacción.

¿Por qué está separado del main offline?
- Este proceso nunca debe mezclarse con el pipeline inicial.
- Queda corriendo de forma continua (no se cierra).
- Necesita estar siempre activo mientras el bot esté en uso.
- Evita volver a procesar todos los JSON cada vez que inicio el bot.

Este main es el “motor vivo” del chatbot.
"""


from bot.manejador_de_bot import DiscordChatbot
from langchain_huggingface import HuggingFaceEmbeddings
from embeddings.gestor_vectores import GestorBaseVectorial

def main():
    bot = DiscordChatbot()
    bot.run()

if __name__ == "__main__":
    main()

# Ejecutarlo por consola con
# python main_bot.py
# para iniciar el bot de Discord.