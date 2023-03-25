from graia.ariadne import Ariadne
from graia.ariadne.model import Friend, Profile
from graia.ariadne.util.async_exec import io_bound

import utils
from admin import error
from app import instance
from chati.chati import UserInfo
from common import friend_chati_session_id


async def on_session_friend_create(app: Ariadne, user_id: int, comment: str, source: str) -> str:
    # 获取好友对象
    friend: Friend | None = await app.get_friend(user_id, cache=True)
    if friend is None:
        raise error.FriendNotFoundError(f"好友 {user_id} 不存在")

    # 获取好友信息
    friend_profile: "Profile" = await friend.get_profile()

    # 获取自己的信息
    profile = await app.get_bot_profile()

    # 删除 chati 会话
    session_id = friend_chati_session_id(app.account, user_id)
    try:
        instance.chati.delete(session_id)
    except RuntimeError:
        pass

    # 创建 chati 会话
    user_info = UserInfo(
        user_id=str(user_id),  # 用户QQ号
        user_nickname=friend.nickname,  # 用户昵称
        user_age=str(friend_profile.age),  # 用户年龄
        user_sex=friend_profile.sex,  # 用户性别
        ai_id=str(app.account),  # AI的QQ号
        ai_nickname=profile.nickname,  # AI昵称
        ai_age=str(profile.age),  # AI年龄
        ai_sex=profile.sex,  # AI性别
        add_source=source,  # 加好友时的来源
        add_comment=comment,  # 加好友时的附加消息
    )
    resp = await utils.create_session_chati(session_id, user_info)

    # 发送 chati 的回复给好友
    await app.send_friend_message(user_id, resp.msg)

    return resp.msg


async def on_session_friend_inherit(app: Ariadne, user_id: int, memo: str, history: str) -> None:
    # 获取好友对象
    friend: Friend | None = await app.get_friend(user_id, cache=True)
    if friend is None:
        raise error.FriendNotFoundError(f"好友 {user_id} 不存在")

    # 获取好友信息
    friend_profile: "Profile" = await friend.get_profile()

    # 获取自己的信息
    profile = await app.get_bot_profile()

    # 删除 chati 会话
    session_id = friend_chati_session_id(app.account, user_id)
    try:
        instance.chati.delete(session_id)
    except RuntimeError:
        pass

    # 继承 chati 会话
    user_info = UserInfo(
        user_id=str(user_id),  # 用户QQ号
        user_nickname=friend.nickname,  # 用户昵称
        user_age=str(friend_profile.age),  # 用户年龄
        user_sex=friend_profile.sex,  # 用户性别
        ai_id=str(app.account),  # AI的QQ号
        ai_nickname=profile.nickname,  # AI昵称
        ai_age=str(profile.age),  # AI年龄
        ai_sex=profile.sex,  # AI性别
        add_source="",  # 加好友时的来源
        add_comment="",  # 加好友时的附加消息
    )
    await utils.inherit_session_chati(session_id, user_info, memo, history)


async def on_session_friend_send(app: Ariadne, user_id: int, msg: str) -> str:
    # 获取好友对象
    friend: Friend | None = await app.get_friend(user_id, cache=True)
    if friend is None:
        raise error.FriendNotFoundError(f"好友 {user_id} 不存在")

    # 发送消息给 chati
    session_id = friend_chati_session_id(app.account, user_id)
    resp = await utils.send_to_chati(msg, session_id)

    # 发送 chati 的回复给好友
    await app.send_friend_message(user_id, resp.msg)

    return resp.msg