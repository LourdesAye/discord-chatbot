def obtener_prompt_analiza_mensaje(pregunta_abierta,mensaje):
    return f"""
    Estás trabajando como un clasificador de mensajes en un entorno académico de Discord. 
    Tu tarea es determinar si un mensaje es:
    - una NUEVA PREGUNTA
    - una REPREGUNTA (continuación o seguimiento de una pregunta anterior)
    - una RESPUESTA a esa pregunta.

    Dado el siguiente par:
    - Pregunta Abierta: "{pregunta_abierta}"
    - Mensaje: "{mensaje}"

    Responde solo con una de estas opciones:
    PREGUNTA, REPREGUNTA, RESPUESTA
    """