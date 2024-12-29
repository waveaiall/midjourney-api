from mysql.mysql_conn import mysql_client
from datetime import datetime
from pydantic import BaseModel
from loguru import logger


class AuthToken(BaseModel):
    id: int
    token: str
    rateLimit: int
    effective: int
    period: int
    capacity: int = None
    expiredAt: datetime
    updatedAt: datetime
    createdAt: datetime


def selectAllEffective():
    """
    查询所有有效的token进行鉴权和限流
        list: 查询结果列表
    """
    query = f"SELECT * FROM wave_midjourney_auth_token WHERE effective = 1 and expired_at>=now()"
    records = mysql_client.select(query)
    return [AuthToken(id=item[0], token=item[1], rateLimit=item[2], period=item[3], capacity=item[4], effective=item[5], expiredAt=item[6], updatedAt=item[7], createdAt=item[8]) for item in records]


def updateTokenCapacity(token: str, capacity: int):
    """
    更新token的容量
        token: 要更新的token
        capacity: 要更新的容量
    """
    if not capacity:
        logger.warning(
            f"current capacity is {capacity}, means infinite, so no need to update")
        return
    query = f"UPDATE wave_midjourney_auth_token SET capacity = {capacity} WHERE token = '{token}' limit 1"
    mysql_client.update(query, ())


def selectAuthToken(token: str):
    """
    查询token的容量
        token: 要查询的token
    """
    query = f"SELECT * FROM wave_midjourney_auth_token WHERE token = '{token}' limit 1"
    records = mysql_client.select(query)
    return [AuthToken(id=item[0], token=item[1], rateLimit=item[2], period=item[3], capacity=item[4], effective=item[5], expiredAt=item[6], updatedAt=item[7], createdAt=item[8]) for item in records][0]


# insert into wave_midjourney_auth_token value(1, 'abc', 10, 1, now(), now())
if __name__ == "__main__":
    tokens = selectAllEffective()
    print(tokens)
