groq_api_key= "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"

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {groq_api_key}",
    "Content-Type": "application/json"
}

def armate_body(funcion,parametro1,parametro2):
       return {
        "model": "llama3-8b-8192",  # O el modelo que estés usando
        "messages": [
            {"role": "user", "content": funcion(parametro1,parametro2)}
        ],
        "temperature": 0,
    }