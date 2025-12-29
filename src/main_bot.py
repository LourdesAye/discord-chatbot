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
    # GESTIÓN DE LA BASE VECTORIAL DE EMBEDDINGS
    # configuración del modelo de embeddings y gestor de base vectorial
    modelo = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") # modelo liviano y rápido
    gestor_base_vectorial = GestorBaseVectorial(modelo) # gestor de base vectorial para realizar operaciones: crear, buscar y eliminar

    # crear base de datos de vectores una vez persistidos los datos
    vectordb = gestor_base_vectorial.crear_si_no_existe()

    # Opción 2: Forzar actualización si hay cambios en BDD
    #if gestor.existe_base() and gestor.verificar_consistencia():
    #    gestor.crear_si_no_existe(forzar_actualizacion=True)

    # probar búsqueda semántica en embeddings
    if vectordb:
        bot = DiscordChatbot(gestor_base_vectorial=gestor_base_vectorial)
    else:
        # logger.debug(" ❌ Hubo un problema con la base de datos vectorial.")
        exit(1)  # Salir del programa si se carga base de datos vectorial correctamente   
    
    bot.run()

if __name__ == "__main__":
    main()

# Ejecutarlo por consola con
# python main_bot.py
# para iniciar el bot de Discord.