import time

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.event.mirai import NewFriendRequestEvent
import graia.ariadne.exception

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import utils
from app import instance
from chati.chati import UserInfo
from utils import send_to_master
from common import friend_chati_session_id

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[NewFriendRequestEvent]))
async def new_friend_request_listener(app: Ariadne, event: NewFriendRequestEvent):
    session_id = friend_chati_session_id(app.account, event.supplicant)
    profile = await app.get_bot_profile()
    master_cor = utils.send_to_master(
        app,
        f"我收到好友申请\n"
        f"QQ： {event.supplicant}\n"
        f"昵称： {event.nickname}\n"
        f"附加消息： {event.message}"
    )
    user_info = UserInfo(
        user_id=str(event.supplicant),  # 用户QQ号
        user_nickname=event.nickname,  # 用户昵称
        user_age="unknown",  # 用户年龄
        user_sex="unknown",  # 用户性别
        ai_id=str(app.account),  # AI的QQ号
        ai_nickname=profile.nickname,  # AI昵称
        ai_age=str(profile.age),  # AI年龄
        ai_sex=profile.sex,  # AI性别
        add_source="0",  # 加好友时的来源
        add_comment=event.message,  # 加好友时的附加消息
    )
    try:
        instance.chati.delete(session_id)
    except RuntimeError as e:
        pass
    try:
        reply = await utils.create_session_chati(session_id, user_info)
    except RuntimeError as e:
        await master_cor
        await send_to_master(app, f"创建好友会话失败： {e}")
        return
    await master_cor
    await event.accept()
    time.sleep(2)
    friend = await app.get_friend(event.supplicant)
    if friend is None:
        # 获取好友失败
        await send_to_master(app, f"获取好友失败（{event.supplicant}）")
        return
    try:
        await utils.send_friend_message(app, friend, reply.msg)
    except Exception as err:
        await send_to_master(app, f"发送好友消息失败（{event.supplicant}），已放弃: {str(err)}")
        return
    await send_to_master(app, f"已成功同意好友申请（{event.supplicant}）")


@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def friend_message_listener(app: Ariadne, event: FriendMessage):
    session_id = friend_chati_session_id(app.account, event.sender.id)

    try:
        reply = await utils.send_to_chati(event.message_chain.display, session_id)
    except RuntimeError as e:
        await send_to_master(app, f"发送消息给 AI 失败： {e}")
        return
    try:
        await utils.send_friend_message(app, event.sender, reply.msg)
    except Exception as err:
        await send_to_master(app, f"发送好友消息失败（{event.sender.id}），已放弃: {str(err)}")
        return
