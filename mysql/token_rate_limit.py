from mysql.mysql_conn import mysql_client
from datetime import datetime
from pydantic import BaseModel


class AuthToken(BaseModel):
    id: int
    token: str
    rateLimit: int
    effective: int
    period: int
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
    return [AuthToken(id=item[0], token=item[1], rateLimit=item[2], period=item[3], effective=item[4], expiredAt=item[5], updatedAt=item[6], createdAt=item[7]) for item in records]


# insert into wave_midjourney_auth_token value(1, 'abc', 10, 1, now(), now())
if __name__ == "__main__":
    tokens = selectAllEffective()
    print(tokens)
