__version__ = '0.0.1'


from asyncio_throttle import Throttler

from mysql import token_rate_limit

TOKEN_2_LIMIT = {auth_token.token: Throttler(rate_limit=auth_token.rateLimit, period=60) for auth_token in token_rate_limit.selectAllEffective()}


def isValid(token:str):
    return token and token in TOKEN_2_LIMIT


def getThrottler(token:str):
    return TOKEN_2_LIMIT[token]