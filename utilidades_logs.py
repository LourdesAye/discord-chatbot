import logging

def setup_logger(name, log_file):
    logger = logging.getLogger(name)  # Cada proceso tiene su propio logger
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)  
    return logger

#Ejemplo de uso 
# 1 - creación y configuración de logger 
# logger_proceso_grande = setup_logger('proceso_grande', 'log_proceso_grande.txt')
# logger_pequeno_1 = setup_logger('proceso_pequeno_1', 'log_proceso_pequeno_1.txt')
# logger_pequeno_2 = setup_logger('proceso_pequeno_2', 'log_proceso_pequeno_2.txt')

# 2- llamado en funciones o procesamiento 
# logger_proceso_grande.info('Inicio del proceso grande')
# logger_proceso_grande.debug('Inicio del proceso grande')
# logger_pequeno_1.info('Proceso pequeño 1 en ejecución')
# logger_pequeno_1.debug('Proceso pequeño 1 en ejecución')














import logging # permite registrar eventos en un programa

def setup_logging():
    logger = logging.getLogger() #se define un logger para manejar los registros.
    logger.setLevel(logging.DEBUG)  # nivel de logging (DEBUG, INFO, etc.)

    # Redirigir a un archivo para la carga de la base de datos
    file_handler_1 = logging.FileHandler('log_carga_base_de_datos.txt', encoding='utf-8') # Crea un manejador de archivos que escribirá los registros en log_carga_base_de_datos.txt
    file_handler_1.setLevel(logging.DEBUG) 
    formatter_1 = logging.Formatter('%(asctime)s - %(message)s') # Define un formateador, estableciendo que cada línea del archivo incluirá la fecha y hora (asctime) y el mensaje.
    file_handler_1.setFormatter(formatter_1) # Aplica el formato al manejador.
    logger.addHandler(file_handler_1) # Agrega el manejador al logger, asegurando que los mensajes se registren en log_carga_base_de_datos.txt.

    # Redirigir a un archivo para el procesamiento de los mensajes
    file_handler_2 = logging.FileHandler('log_procesamiento_mensajes.txt', encoding='utf-8')
    file_handler_2.setLevel(logging.DEBUG)
    formatter_2 = logging.Formatter('%(asctime)s - %(message)s')
    file_handler_2.setFormatter(formatter_2)
    logger.addHandler(file_handler_2)

    return logger