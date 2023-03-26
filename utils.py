import time

import graia.ariadne.exception
from graia.ariadne import Ariadne
from graia.ariadne.model import Friend
from graia.ariadne.util.async_exec import io_bound
from loguru import logger

from app import instance
from chati.chati import SessionMessageResponse, UserInfo


async def send_to_master(app: Ariadne, msg: str):
    for master in instance.config.masters:
        try:
            friend = await app.get_friend(master, assertion=True, cache=True)
        except ValueError:
            continue
        try:
            await app.send_message(friend, msg)
        except Exception:
            continue


async def send_friend_message(app: Ariadne, friend: Friend, msg: str):
    # 尝试发送三次
    for i in range(3):
        try:
            await app.send_message(friend, msg)
            return
        except graia.ariadne.exception.RemoteException as err:
            logger.error(f"发送消息给好友失败（{friend.id}）: {str(err)}")
            await send_to_master(app, f"发送消息给好友失败（{friend.id}）: {str(err)}")
            if i == 2:
                raise err
            time.sleep((i + 1) * 3)
            continue


@io_bound
def send_to_chati(msg: str, session_id: str) -> SessionMessageResponse:
    instance.chati.send(msg, session_id)
    resp = instance.chati.get_until_end(session_id)
    return resp


@io_bound
def create_session_chati(session_id: str, user_info: UserInfo) -> SessionMessageResponse:
    instance.chati.create_friend(session_id, user_info)
    resp = instance.chati.get_until_end(session_id)
    return resp


@io_bound
def inherit_session_chati(session_id: str, user_info: UserInfo, memo: str, history: str) -> SessionMessageResponse:
    instance.chati.inherit_friend(session_id, user_info, memo, history)
    resp = instance.chati.get_until_end(session_id)
    return resp
