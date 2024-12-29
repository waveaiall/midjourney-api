__version__ = '0.0.1'

from asyncio_throttle import Throttler
from loguru import logger

from mysql import token_rate_limit


def refreshToken():
    global TOKEN_2_LIMIT, TOKEN_2_ENTITY
    TOKEN_2_LIMIT = {auth_token.token: Throttler(rate_limit=auth_token.rateLimit, capacity=auth_token.capacity,
                                                 period=auth_token.period) for auth_token in token_rate_limit.selectAllEffective()}
    TOKEN_2_ENTITY = {auth_token.token: auth_token for auth_token in token_rate_limit.selectAllEffective()}
    logger.info(
        f'refresh token info {TOKEN_2_LIMIT.keys()} limit {TOKEN_2_LIMIT.values()}')


TOKEN_2_LIMIT = {}
TOKEN_2_ENTITY = {}
refreshToken()


def is_valid(token: str):
    return token and token in TOKEN_2_LIMIT


def is_exceed_capacity(token: str):
    capacity = TOKEN_2_ENTITY[token].capacity
    if capacity == -1:
        return False
    else:
        return capacity == 0


def update_capacity_mem_and_db(token: str, capacity: int):
    token_rate_limit.updateTokenCapacity(token, capacity)
    TOKEN_2_ENTITY[token].capacity = capacity


def getThrottler(token: str):
    return TOKEN_2_LIMIT[token]


if __name__ == "__main__":
    refreshToken()
    print(TOKEN_2_LIMIT)
