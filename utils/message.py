import time

import graia.ariadne.exception
from graia.amnesia.message import MessageChain
from graia.ariadne import Ariadne
from graia.ariadne.model import Friend, Group
from loguru import logger

from app import instance


async def send_to_master(app: Ariadne, msg: str | MessageChain):
    for master in instance.config.accounts_map[app.account].masters:
        try:
            friend = await app.get_friend(master, assertion=True, cache=True)
        except ValueError:
            continue
        try:
            await app.send_friend_message(friend, msg)
        except Exception:
            continue


async def send_friend_message(app: Ariadne, friend: Friend, message_chain: MessageChain):
    # 尝试发送三次
    for i in range(3):
        try:
            return await app.send_friend_message(friend, message_chain)
        except graia.ariadne.exception.RemoteException as err:
            logger.error(f"发送消息给好友失败（{friend.id}）: {str(err)}")
            await send_to_master(app, f"发送消息给好友失败（{friend.id}）: {str(err)}")
            if i == 2:
                raise err
            time.sleep((i + 1) * 3)
            continue


async def send_group_message(app: Ariadne, group: Group, message_chain: MessageChain):
    # 尝试发送三次
    for i in range(3):
        try:
            return await app.send_group_message(group, message_chain)
        except graia.ariadne.exception.RemoteException as err:
            logger.error(f"发送消息给群组失败（{group.id}）: {str(err)}")
            await send_to_master(app, f"发送消息给群组失败（{group.id}）: {str(err)}")
            if i == 2:
                raise err
            time.sleep((i + 1) * 3)
            continue
