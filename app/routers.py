from fastapi import APIRouter, HTTPException, UploadFile, Request, Depends, Header

import traceback
from lib.api import discord
from lib.api.discord import TriggerType
from util._queue import taskqueue
from .handler import prompt_handler, unique_id
from .schema import (
    TriggerExpandIn,
    TriggerImagineIn,
    TriggerUVIn,
    TriggerResetIn,
    QueueReleaseIn,
    TriggerResponse,
    TriggerZoomOutIn,
    UploadResponse,
    TriggerDescribeIn,
    SendMessageResponse,
    SendMessageIn,
    CallbackResponse,
    GenerateResult,
)
from loguru import logger
import json
from mysql.stage_result_mapper import select_by_trigger, upsert_pic_result, upsert_with_token
from auth import is_valid, get_throttler, is_exceed_capacity, update_capacity_mem_and_db, get_auth_token


router = APIRouter()


async def check_token(token: str = Header(None)):
    if not is_valid(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if is_exceed_capacity(token):
        raise HTTPException(status_code=429, detail="Exceed Capacity Limit")

@router.post("/midjourney/callback", response_model=CallbackResponse)
async def callback(request: Request):
    body = await request.body()  # This will return the body as bytes
    body_str = body.decode("utf-8")  # Convert bytes to a string
    logger.info(body_str)
    body_json = json.loads(body_str)
    stage = body_json['type']
    trigger_id = body_json["trigger_id"]
    msg_id = body_json["id"]
    if stage == 'end':
        filename = body_json["attachments"][0]["filename"]
        msg_hash = body_json["attachments"][0]["filename"].split(
            "_")[-1].split(".")[0]
        url = body_json["attachments"][0]["url"]
        logger.info(f'trigger_id={trigger_id}')
        logger.info(f'msg_id={msg_id}')
        logger.info(f'filename={filename}')
        logger.info(f'msg_hash={msg_hash}')
        logger.info(f'url={url}')
        upsert_pic_result(trigger_id, stage, url, msg_id, msg_hash)
    else:
        logger.info(
            '=======================>generating=======================>')
        upsert_pic_result(trigger_id, stage, '', msg_id, '')
    return {'code': 0, 'message': 'succeed'}



@router.get('/midjourney/result/{trigger_id}', response_model=GenerateResult, dependencies=[Depends(check_token)])
async def get_result(trigger_id: str):
    try:
        data = select_by_trigger(trigger_id)
        if not data:
            return {'code': -2, 'message': 'no trigger task, please retry the prompt!'}
        else:
            row = data[0]
            return {'code': 0, 'message': row[2], 'data': row[3]}
    except Exception as e:
        logger.error('get result meet some error! msg={e}')
        traceback.print_exc()  # 打印堆栈跟踪信息
        return {'code': -1, 'message': 'get result meet some error!'}


@router.get('/midjourney/upscale/{trigger_id}/{index}', response_model=TriggerResponse, dependencies=[Depends(check_token)])
async def upscale_by_trigger(trigger_id: str, index: int, token: str = Header(None)):
    async with get_throttler(token):
        try:
            data = select_by_trigger(trigger_id)
            new_trigger_id = str(unique_id())
            if not data:
                return {'message': 'no trigger task, please retry the prompt!', 'trigger_id': trigger_id}
            else:
                row = data[0]
                upsert_with_token(new_trigger_id,'request', token)
                return await upscale(TriggerUVIn(index=index, msg_id=row[4], msg_hash=row[5], trigger_id=new_trigger_id))
        except Exception as e:
            logger.error(f'get result meet some error! msg={e}')
            traceback.print_exc()  # 打印堆栈跟踪信息
            return {'message': 'upscale meet some error!', 'trigger_id': trigger_id}

@router.post("/imagine", response_model=TriggerResponse, dependencies=[Depends(check_token)])
async def imagine(body: TriggerImagineIn, token: str = Header(None)):
    async with get_throttler(token):
        trigger_id, prompt = prompt_handler(body.prompt, body.picurl)
        trigger_type = TriggerType.generate.value
        upsert_with_token(trigger_id, 'request', token)
        current_capacity = get_auth_token(token).capacity
        if current_capacity:
            current_capacity -= 1
        if current_capacity and current_capacity <=0:
            raise HTTPException(status_code=429, detail="Exceed Capacity Limit")
        update_capacity_mem_and_db(token, current_capacity)
        
        taskqueue.put(trigger_id, discord.generate, prompt)
        
        return {"trigger_id": trigger_id, "trigger_type": trigger_type}


@router.post("/upscale", response_model=TriggerResponse)
async def upscale(body: TriggerUVIn):
    print(body)
    trigger_id = body.trigger_id
    trigger_type = TriggerType.upscale.value

    taskqueue.put(trigger_id, discord.upscale, **body.dict())
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


@router.post("/variation", response_model=TriggerResponse)
async def variation(body: TriggerUVIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.variation.value

    taskqueue.put(trigger_id, discord.variation, **body.dict())
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


@router.post("/reset", response_model=TriggerResponse)
async def reset(body: TriggerResetIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.reset.value

    taskqueue.put(trigger_id, discord.reset, **body.dict())
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


@router.post("/describe", response_model=TriggerResponse)
async def describe(body: TriggerDescribeIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.describe.value

    taskqueue.put(trigger_id, discord.describe, **body.dict())
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


@router.post("/upload", response_model=UploadResponse)
async def upload_attachment(file: UploadFile):
    if not file.content_type.startswith("image/"):
        return {"message": "must image"}

    trigger_id = str(unique_id())
    filename = f"{trigger_id}.jpg"
    file_size = file.size
    attachment = await discord.upload_attachment(filename, file_size, await file.read())
    if not (attachment and attachment.get("upload_url")):
        return {"message": "Failed to upload image"}

    return {
        "upload_filename": attachment.get("upload_filename"),
        "upload_url": attachment.get("upload_url"),
        "trigger_id": trigger_id,
    }


@router.post("/message", response_model=SendMessageResponse)
async def send_message(body: SendMessageIn):
    picurl = await discord.send_attachment_message(body.upload_filename)
    if not picurl:
        return {"message": "Failed to send message"}

    return {"picurl": picurl}


@router.post("/queue/release", response_model=TriggerResponse)
async def queue_release(body: QueueReleaseIn):
    """bot 清除队列任务"""
    taskqueue.pop(body.trigger_id)

    return body


@router.post("/solo_variation", response_model=TriggerResponse)
async def solo_variation(body: TriggerUVIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.solo_variation.value
    taskqueue.put(trigger_id, discord.solo_variation, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


@router.post("/solo_low_variation", response_model=TriggerResponse)
async def solo_low_variation(body: TriggerUVIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.solo_low_variation.value
    taskqueue.put(trigger_id, discord.solo_low_variation, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


@router.post("/solo_high_variation", response_model=TriggerResponse)
async def solo_high_variation(body: TriggerUVIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.solo_high_variation.value
    taskqueue.put(trigger_id, discord.solo_high_variation, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


@router.post("/expand", response_model=TriggerResponse)
async def expand(body: TriggerExpandIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.expand.value
    taskqueue.put(trigger_id, discord.expand, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}


@router.post("/zoomout", response_model=TriggerResponse)
async def zoomout(body: TriggerZoomOutIn):
    trigger_id = body.trigger_id
    trigger_type = TriggerType.zoomout.value
    taskqueue.put(trigger_id, discord.zoomout, **body.dict())

    # 返回结果
    return {"trigger_id": trigger_id, "trigger_type": trigger_type}
