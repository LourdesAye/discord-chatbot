def obtener_prompt_analiza_mensaje(pregunta_abierta,mensaje):
    return f""" Eres un clasificador conversacional entrenado para analizar mensajes en un canal educativo de Discord.

    Se te dará:
    - Una pregunta previa de un estudiante.
    - Un nuevo mensaje que apareció después.

    Tu tarea es clasificar si el nuevo mensaje es:
    (A) una **respuesta** a esa pregunta anterior,
    (B) una **pregunta nueva e independiente**.

    🔒 Restricciones:
    - Si el mensaje contiene una nueva duda técnica o de herramientas distinta al tema de la pregunta anterior, clasifícalo como (B).
    - Si el mensaje parece responder, sugerir soluciones o comentar sobre el contenido de la pregunta, clasifícalo como (A).

    Devuelve **solo una palabra en mayúsculas** entre: `RESPUESTA`, `PREGUNTA`.

    ---

    🧠 Pregunta previa:
    "{pregunta_abierta}"

    ✉️ Mensaje nuevo:
    "{mensaje}"

    """
