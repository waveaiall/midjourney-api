__version__ = '0.0.1'

from asyncio_throttle import Throttler
from loguru import logger

from mysql import token_rate_limit


def refreshToken():
    global TOKEN_2_LIMIT
    TOKEN_2_LIMIT = {auth_token.token: Throttler(rate_limit=auth_token.rateLimit, period=auth_token.period) for auth_token in token_rate_limit.selectAllEffective()}
    logger.info(
        f'refresh token info {TOKEN_2_LIMIT.keys()} limit {TOKEN_2_LIMIT.values()}')


TOKEN_2_LIMIT = {}
refreshToken()


def is_valid(token: str):
    return token and token in TOKEN_2_LIMIT


def is_exceed_capacity(token: str):
    capacity = get_auth_token(token).capacity
    if capacity is None:
        return False
    else:
        return capacity <= 0


def update_capacity_mem_and_db(token: str, capacity: int):
    token_rate_limit.updateTokenCapacity(token, capacity)


def get_throttler(token: str):
    return TOKEN_2_LIMIT[token]

def get_auth_token(token: str):
    return token_rate_limit.selectAuthToken(token)

if __name__ == "__main__":
    refreshToken()
    print(TOKEN_2_LIMIT)
