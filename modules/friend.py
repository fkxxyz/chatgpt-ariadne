from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.event.mirai import NewFriendRequestEvent
from graia.ariadne.model import Profile
from graia.ariadne.util.async_exec import io_bound

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from app import instance
from chati.chati import UserInfo
from utils import send_to_master

channel = Channel.current()


def chati_session_id(supplicant: int) -> str:
    return f"friend-{supplicant}"


@io_bound
def create_friend_context(self_id: int, profile: Profile, event: NewFriendRequestEvent):
    session_id = chati_session_id(event.supplicant)

    instance.chati.create_friend(session_id, UserInfo(
        user_id=str(event.supplicant),  # 用户QQ号
        user_nickname=event.nickname,  # 用户昵称
        user_age="unknown",  # 用户年龄
        user_sex="unknown",  # 用户性别
        ai_id=str(self_id),  # AI的QQ号
        ai_nickname=profile.nickname,  # AI昵称
        ai_age=str(profile.age),  # AI年龄
        ai_sex=profile.sex,  # AI性别
        add_source="0",  # 加好友时的来源
        add_comment=event.message,  # 加好友时的附加消息
    ))
    resp = instance.chati.get_until_end(session_id)
    return resp.msg


@io_bound
def send_friend_message(event: FriendMessage):
    session_id = chati_session_id(event.sender.id)

    instance.chati.send(event.message_chain.display, session_id)
    resp = instance.chati.get_until_end(session_id)
    return resp.msg


@channel.use(ListenerSchema(listening_events=[NewFriendRequestEvent]))
async def new_friend_request_listener(app: Ariadne, event: NewFriendRequestEvent):
    profile = await app.get_bot_profile()
    try:
        message = await create_friend_context(app.account, profile, event)
    except RuntimeError as e:
        await send_to_master(app, f"创建好友会话失败： {e}")
        return
    await event.accept()
    friend = await app.get_friend(event.supplicant)
    if friend is None:
        assert False  # "好友不存在"
    await app.send_message(friend, message)


@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def friend_message_listener(app: Ariadne, event: FriendMessage):
    try:
        reply = await send_friend_message(event)
    except RuntimeError as e:
        await send_to_master(app, f"发送好友消息失败： {e}")
        return
    await app.send_message(event.sender, reply)
