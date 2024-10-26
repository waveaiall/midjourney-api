from os import getenv
from loguru import logger
from dotenv import load_dotenv

__version__ = '0.0.1'

# env config load
load_dotenv()

MYSQL_HOST = getenv("MYSQL_HOST")
MYSQL_PORT = getenv("MYSQL_PORT")
MYSQL_USER = getenv("MYSQL_USER")
MYSQL_PWD = getenv("MYSQL_PWD")
