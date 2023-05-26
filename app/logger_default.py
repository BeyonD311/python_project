import logging

__all__ = ["get_logger"]

FROMATTER = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

def file_handler(filename: str) -> logging.FileHandler:
    """ Обработчик для записи логов в файл """
    file_handler = logging.FileHandler(filename=f"{filename}.log", mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(FROMATTER)
    return file_handler

def get_logger(name) -> logging.Logger:
    """ Получение экземпляра Logger """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler(f"log/{name}"))
    return logger