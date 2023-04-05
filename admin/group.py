from graia.amnesia.message import MessageChain
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Group, GroupConfig

import utils.message
import utils.chati
from admin import error
from app import instance
from chati.chati import GroupInfo
from common import group_chati_session_id


async def on_session_group_create(app: Ariadne, group_id: int) -> str:
    # 获取群组对象
    group: Group | None = await app.get_group(group_id, cache=True)
    if group is None:
        raise error.FriendNotFoundError(f"群组 {group_id} 不存在")

    # 获取群组信息
    group_config: GroupConfig = await group.get_config()

    # 获取自己的信息
    profile = await app.get_bot_profile()

    # 删除 chati 会话
    session_id = group_chati_session_id(app.account, group_id)
    try:
        instance.chati.delete(session_id)
    except RuntimeError:
        pass

    # 创建 chati 会话
    group_info = GroupInfo(
        group_id=str(group.id),  # 群号
        group_name=group.name,  # 群名
        group_announcement=group_config.announcement,  # 群公告
        ai_id=str(app.account),  # AI的QQ号
        ai_nickname=profile.nickname,  # AI昵称
        ai_age=str(profile.age),  # AI年龄
        ai_sex=profile.sex,  # AI性别
        welcome_prompt="",
    )
    resp = await utils.chati.create_session_group_chati(session_id, group_info)

    # 发送 chati 的回复给群组
    try:
        await utils.message.send_group_message(app, group, resp)
    except Exception as err:
        await utils.message.send_to_master(app, f"发送群组消息失败（{group.id}），已放弃: {str(err)}")
        return resp

    return resp


async def on_session_group_inherit(app: Ariadne, group_id: int, memo: str, history: str) -> None:
    # 获取群组对象
    group: Group | None = await app.get_group(group_id, cache=True)
    if group is None:
        raise error.FriendNotFoundError(f"群组 {group_id} 不存在")

    # 获取群组信息
    group_config: GroupConfig = await group.get_config()

    # 获取自己的信息
    profile = await app.get_bot_profile()

    # 删除 chati 会话
    session_id = group_chati_session_id(app.account, group_id)
    try:
        instance.chati.delete(session_id)
    except RuntimeError:
        pass

    # 继承 chati 会话
    group_info = GroupInfo(
        group_id=str(group.id),  # 群号
        group_name=group.name,  # 群名
        group_announcement=group_config.announcement,  # 群公告
        ai_id=str(app.account),  # AI的QQ号
        ai_nickname=profile.nickname,  # AI昵称
        ai_age=str(profile.age),  # AI年龄
        ai_sex=profile.sex,  # AI性别
        welcome_prompt="",
    )
    await utils.chati.inherit_session_group_chati(session_id, group_info, memo, history)


async def on_session_group_send(app: Ariadne, group_id: int, msg: str) -> str:
    # 获取群组对象
    group: Group | None = await app.get_group(group_id, cache=True)
    if group is None:
        raise error.FriendNotFoundError(f"群组 {group_id} 不存在")

    # 发送消息给 chati
    session_id = group_chati_session_id(app.account, group_id)
    resp = await utils.chati.send_to_chati(msg, session_id)

    # 发送 chati 的回复给群组
    message = [Plain(' ' + resp)]
    message = await instance.middlewares.execute(message)
    try:
        await utils.message.send_group_message(app, group, MessageChain(message))
    except Exception as err:
        await utils.message.send_to_master(app, f"发送群组消息失败（{group.id}），已放弃: {str(err)}")
        return resp

    return resp


async def on_group_welcome_prompt(app: Ariadne, group_id: int, prompt: str):
    # 获取群组对象
    group: Group | None = await app.get_group(group_id, cache=True)
    if group is None:
        raise error.FriendNotFoundError(f"群组 {group_id} 不存在")

    session_id = group_chati_session_id(app.account, group_id)

    instance.chati.set_params(session_id, {
        "welcome_prompt": prompt,
    })
