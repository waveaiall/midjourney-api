__version__ = '0.0.1'


from apscheduler.schedulers.background import BackgroundScheduler
from asyncio_throttle import Throttler
from loguru import logger

from mysql import token_rate_limit

TOKEN_2_LIMIT = {auth_token.token: Throttler(rate_limit=auth_token.rateLimit, period=60) for auth_token in token_rate_limit.selectAllEffective()}
scheduler = BackgroundScheduler()

def refreshToken():
     global TOKEN_2_LIMIT 
     TOKEN_2_LIMIT = {auth_token.token: Throttler(rate_limit=auth_token.rateLimit, period=60) for auth_token in token_rate_limit.selectAllEffective()}
     logger.info(f'refresh token info {TOKEN_2_LIMIT.keys()} limit {TOKEN_2_LIMIT.values()}')

def isValid(token:str):
    return token and token in TOKEN_2_LIMIT


def getThrottler(token:str):
    return TOKEN_2_LIMIT[token]

# 示例 4: 每天的每隔 5 分钟执行一次
scheduler.add_job(refreshToken, 'cron', minute='*/5')

scheduler.start()