from mysql.mysql_conn import mysql_client
from datetime import datetime


def upsert_origin_pic_result(trigger_id: str, stage: str, pic_url: str, msg_id: str, msg_hash: str):
    """
    插入或更新 stage_result 表中的数据

    Args:
        trigger_id (str): 触发器 ID
        stage (str): 阶段名称
        pic_url (str): 结果 URL (图片地址)
        msg_id (str): message id
        msg_hash (str): message hash
        status (str): 状态
        msg (str): 消息
    """
    query = "INSERT INTO wave_midjourney_stage_result (trigger_id, stage, pic_url, msg_id, msg_hash, origin_pic_url, origin_msg_id, origin_msg_hash, updated_at, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE stage = VALUES(stage), pic_url = VALUES(pic_url), msg_id = VALUES(msg_id), msg_hash=VALUES(msg_hash), origin_pic_url = VALUES(origin_pic_url), origin_msg_id = VALUES(origin_msg_id), origin_msg_hash=VALUES(origin_msg_hash)"
    data = (trigger_id, stage, pic_url, msg_id, msg_hash, pic_url, msg_id, msg_hash, datetime.now(), datetime.now())
    mysql_client.insert(query, data)

def upsert_pic_result(trigger_id: str, stage: str, pic_url: str, msg_id: str, msg_hash: str):
    """
    插入或更新 stage_result 表中的数据

    Args:
        trigger_id (str): 触发器 ID
        stage (str): 阶段名称
        pic_url (str): 结果 URL (图片地址)
        msg_id (str): message id
        msg_hash (str): message hash
        status (str): 状态
        msg (str): 消息
    """
    query = "INSERT INTO wave_midjourney_stage_result (trigger_id, stage, pic_url, msg_id, msg_hash, updated_at, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE stage = VALUES(stage), pic_url = VALUES(pic_url), msg_id = VALUES(msg_id), msg_hash=VALUES(msg_hash)"
    data = (trigger_id, stage, pic_url, msg_id, msg_hash, datetime.now(), datetime.now())
    mysql_client.insert(query, data)


def upsert_with_token(trigger_id: str, stage: str, token: str, prompt: str):
    """
    插入或更新 stage_result 表中的数据

    Args:
        trigger_id (str): 触发器 ID
        stage (str): 阶段名称
        token (str): 查询token
        prompt (str): 查询prompt
    """
    query = "INSERT INTO wave_midjourney_stage_result (trigger_id, stage, token, prompt, updated_at, created_at) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE stage = VALUES(stage)"
    data = (trigger_id, stage, token, prompt, datetime.now(), datetime.now())
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
    return mysql_client.select(query)