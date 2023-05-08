import requests
from graia.amnesia.message import MessageChain
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Profile

import utils.message
import utils.chati
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
    friend_profile: "Profile" = await app.get_friend_profile(friend)

    # 获取自己的信息
    profile = await app.get_bot_profile()

    # 删除 chati 会话
    session_id = friend_chati_session_id(app.account, user_id)
    try:
        await utils.chati.delete(session_id)
    except requests.HTTPError:
        pass

    # 创建 chati 会话
    user_info = UserInfo(
        user_id=str(user_id),  # 用户QQ号
        user_nickname=friend_profile.nickname,  # 用户昵称
        user_age=str(friend_profile.age),  # 用户年龄
        user_sex=friend_profile.sex,  # 用户性别
        ai_id=str(app.account),  # AI的QQ号
        ai_nickname=profile.nickname,  # AI昵称
        ai_age=str(profile.age),  # AI年龄
        ai_sex=profile.sex,  # AI性别
        add_source=source,  # 加好友时的来源
        add_comment=comment,  # 加好友时的附加消息
    )
    type_ = instance.config.accounts_map[app.account].friend_type
    resp = await utils.chati.create_session_friend_chati(session_id, type_, user_info)

    # 发送 chati 的回复给好友
    try:
        await utils.message.send_friend_message(app, friend, resp)
    except Exception as err:
        await utils.message.send_to_master(app, f"发送好友消息失败（{friend.id}），已放弃: {str(err)}")
        return resp

    return resp


async def on_session_friend_inherit(app: Ariadne, user_id: int, memo: str, history: str) -> None:
    # 获取好友对象
    friend: Friend | None = await app.get_friend(user_id, cache=True)
    if friend is None:
        raise error.FriendNotFoundError(f"好友 {user_id} 不存在")

    # 获取好友信息
    friend_profile: "Profile" = await app.get_friend_profile(friend)

    # 获取自己的信息
    profile = await app.get_bot_profile()

    # 删除 chati 会话
    session_id = friend_chati_session_id(app.account, user_id)
    try:
        await utils.chati.delete(session_id)
    except requests.HTTPError:
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
    type_ = instance.config.accounts_map[app.account].friend_type
    await utils.chati.inherit_session_friend_chati(session_id, type_, user_info, memo, history)


async def on_session_friend_send(app: Ariadne, user_id: int, msg: str) -> str:
    # 获取好友对象
    friend: Friend | None = await app.get_friend(user_id, cache=True)
    if friend is None:
        raise error.FriendNotFoundError(f"好友 {user_id} 不存在")

    # 发送消息给 chati
    session_id = friend_chati_session_id(app.account, user_id)
    resp = await utils.chati.send_to_chati(msg, session_id)

    # 发送 chati 的回复给好友
    message = [Plain(resp)]
    exclude_set = instance.config.accounts_map[app.account].disabled_middlewares_map
    message = await instance.middlewares.execute_out(message, exclude_set)
    try:
        await utils.message.send_friend_message(app, friend, MessageChain(message))
    except Exception as err:
        await utils.message.send_to_master(app, f"发送好友消息失败（{friend.id}），已放弃: {str(err)}")
        return resp

    return resp
