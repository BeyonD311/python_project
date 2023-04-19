import logging

__all__ = ["get_logger"]

def get_file_handler(filename):
    file_handler = logging.FileHandler(filename=filename, mode="w")
    file_handler.setLevel(logging.DEBUG)
    return file_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(f"log/{name}"))
    return logger