from config import *

import logging.config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('logfile.log')

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
def debug_request(f):
    def inner(*args, **kwargs):
        try:
            logger.info(f"{datetime.datetime.now().strftime('%d.%b %Y %H:%M:%S')} Обращение в функцию {f.__name__}")
            return f(*args, **kwargs)
        except:
            logger.exception(f"{datetime.datetime.now().strftime('%d.%b %Y %H:%M:%S')} Ошибка в разработчике {f.__name__}")
            raise
    return inner