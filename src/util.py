import logging
import logging.handlers


class TipBotException(Exception):
    def __init__(self, error_type):
        self.error_type = error_type
        Exception.__init__(self)

    def __str__(self):
        return repr(self.error_type)


def get_logger(name):
    formatter = logging.Formatter('%(asctime)s [%(name)s] -%(levelname)s- %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.handlers.TimedRotatingFileHandler('debug.log', when='midnight', backupCount=0)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger


def get_numerical_emoji(num):
    num_str = str(num)
    num_str = num_str.replace('0', ':zero:')
    num_str = num_str.replace('1', ':one:')
    num_str = num_str.replace('2', ':two:')
    num_str = num_str.replace('3', ':three:')
    num_str = num_str.replace('4', ':four:')
    num_str = num_str.replace('5', ':five:')
    num_str = num_str.replace('6', ':six:')
    num_str = num_str.replace('7', ':seven:')
    num_str = num_str.replace('8', ':eight:')
    num_str = num_str.replace('9', ':nine:')
    return num_str
