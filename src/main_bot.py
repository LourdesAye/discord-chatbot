from bot.manejador_de_bot import DiscordChatbot
from langchain_huggingface import HuggingFaceEmbeddings
from embeddings.gestor_vectores import GestorBaseVectorial

def main():
    bot = DiscordChatbot()
    bot.run()

if __name__ == "__main__":
    main()
