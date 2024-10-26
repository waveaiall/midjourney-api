# coding=utf-8

import pymysql
from loguru import logger
import time

from mysql import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD

def retry(max_retries, delay=1, backoff=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.error(f"Error: {e}")
                    retries += 1
                    time.sleep(delay)
                    delay *= backoff
            raise Exception(f"Max retries ({max_retries}) reached. Unable to execute {func.__name__}.")
        return wrapper
    return decorator

class MysqlClient():
    def __init__(self, host, user, password, db, port: int = 3306) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        logger.warning(f'start connect to host={host} port={port} user={user}!')
        self.conn = self._connect()
        logger.warning(f'complete connect to host={host} port={port} user={user}!')

    def _connect(self):
        return pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.password, db=self.db)
    
    def __del__(self):
        if self.conn:
            self.conn.close()

    def insert(self, query: str, data: tuple):
        self.try_and_reconnect()
        with self.conn.cursor() as cursor:
            # execute
            size = cursor.execute(query, data)
            logger.debug(f'execute query={query} data={data} result={size}')
            self.conn.commit()
        return size

    def get_last_id(self):
        return self.conn.insert_id()

    @retry(max_retries=3)
    def try_and_reconnect(self):
        try:
            self.conn.ping(reconnect=False)
        except Exception as e:
            logger.error(f'ping to mysql failed {e}')
            self.conn = self._connect()
            logger.warning(f'reconnect mysql connection!')
            

    def select(self, query):
        self.try_and_reconnect()
        with self.conn.cursor() as cursor:
            # execute
            cursor.execute(query)
            results = cursor.fetchall()
            logger.debug(f'execute query={query} result={results}')
        return results

    def update(self, query, data: tuple):
        self.try_and_reconnect()
        with self.conn.cursor() as cursor:
            # execute
            size = cursor.execute(query, data)
            logger.debug(f'execute query={query} data={data} result={size}')
            self.conn.commit()
        return size


mysql_client = MysqlClient(host=MYSQL_HOST,
                           port=int(MYSQL_PORT),
                           user=MYSQL_USER,
                           password=MYSQL_PWD,
                           db='wave')

if __name__ == "__main__":
    logger.info(MYSQL_HOST)
    mysql_client.select('select * from wave_wx_access_token limit 1')
