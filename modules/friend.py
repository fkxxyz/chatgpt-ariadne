from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.event.mirai import NewFriendRequestEvent

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import utils
from chati.chati import UserInfo
from utils import send_to_master
from common import friend_chati_session_id

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[NewFriendRequestEvent]))
async def new_friend_request_listener(app: Ariadne, event: NewFriendRequestEvent):
    session_id = friend_chati_session_id(app.account, event.supplicant)
    profile = await app.get_bot_profile()
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
        reply = await utils.create_session_chati(session_id, user_info)
    except RuntimeError as e:
        await send_to_master(app, f"创建好友会话失败： {e}")
        return
    await event.accept()
    friend = await app.get_friend(event.supplicant)
    if friend is None:
        assert False  # "好友不存在"
    await app.send_message(friend, reply.msg)


@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def friend_message_listener(app: Ariadne, event: FriendMessage):
    session_id = friend_chati_session_id(app.account, event.sender.id)

    try:
        reply = await utils.send_to_chati(event.message_chain.display, session_id)
    except RuntimeError as e:
        await send_to_master(app, f"发送好友消息失败： {e}")
        return
    await app.send_message(event.sender, reply.msg)
