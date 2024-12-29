__version__ = '0.0.1'

from asyncio_throttle import Throttler
from loguru import logger

from mysql import token_rate_limit

TOKEN_2_LIMIT = {auth_token.token: Throttler(rate_limit=auth_token.rateLimit, period=auth_token.period,
                                             capacity=auth_token.capacity) for auth_token in token_rate_limit.selectAllEffective()}


def refreshToken():
    global TOKEN_2_LIMIT
    TOKEN_2_LIMIT = {auth_token.token: Throttler(rate_limit=auth_token.rateLimit, period=auth_token.period,
                                                 capacity=auth_token.capacity) for auth_token in token_rate_limit.selectAllEffective()}
    logger.info(
        f'refresh token info {TOKEN_2_LIMIT.keys()} limit {TOKEN_2_LIMIT.values()}')


def isValid(token: str):
    return token and token in TOKEN_2_LIMIT


def isExceedCapacity(token: str):
    count = TOKEN_2_LIMIT[token].count
    if count == -1:
        return True
    else:
        return count >= 1

def update_capacity_mem_and_db(token: str, capacity: int):
    token_rate_limit.updateTokenCapacity(token, capacity)
    TOKEN_2_LIMIT[token].capacity = capacity


def getThrottler(token: str):
    return TOKEN_2_LIMIT[token]

if __name__ == "__main__":
    refreshToken()