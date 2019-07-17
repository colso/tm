import logging
import logging.handlers

def set_logger(logger_name=None):
    if not logger_name:
        logger = logging.getLogger('torr_logger')
    else:
        logger = logginggetLogger(logger_name)

def get_logger(logger_name=None):
    if logger_name:
        return logging.getLogger(logger_name)
    else:
        return logging.getLogger('torr_logger')

def setup(logger, logpath):
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)10s] [%(filename)16s:%(lineno)4s] %(message)s')
    filehandler = logging.handlers.TimedRotatingFileHandler(logpath, when='h', interval=1, backupCount=14)
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    logger.setLevel(logging.DEBUG)