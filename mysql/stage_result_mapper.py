from mysql.mysql_conn import mysql_client
from datetime import datetime


def upsert_pic_result(trigger_id: str, stage: str, pic_url: str):
    """
    插入或更新 stage_result 表中的数据

    Args:
        trigger_id (str): 触发器 ID
        stage (str): 阶段名称
        pic_url (str): 结果 URL (图片地址)
        status (str): 状态
        msg (str): 消息
    """
    query = "INSERT INTO wave_midjourney_stage_result (trigger_id, stage, pic_url, updated_at, created_at) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE stage = VALUES(stage), pic_url = VALUES(pic_url)"
    data = (trigger_id, stage, pic_url, datetime.now(), datetime.now())
    mysql_client.insert(query, data)


def select_by_trigger(trigger_id: str):
    """
    根据 trigger_id 查询 stage_result 表中的数据
    Args:
        trigger_id (str): 触发器 ID
    Returns:
        list: 查询结果列表
    """
    query = f"SELECT * FROM wave_midjourney_stage_result WHERE trigger_id = '{trigger_id}'"
    return mysql_client.select(query)[0]