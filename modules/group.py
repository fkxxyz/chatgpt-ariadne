from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import BotJoinGroupEvent, BotInvitedJoinGroupRequestEvent
from graia.ariadne.message.element import At

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import utils
from app import instance
from chati.chati import GroupInfo
from common import group_chati_session_id

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def group_invite_listener(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    await event.reject("")


@channel.use(ListenerSchema(listening_events=[BotJoinGroupEvent]))
async def group_add_listener(app: Ariadne, event: BotJoinGroupEvent):
    session_id = group_chati_session_id(app.account, event.group.id)
    group_config = await app.get_group_config(event.group)
    profile = await app.get_bot_profile()
    master_cor = utils.send_to_master(
        app,
        f"我已加入群组\n"
        f"群号： {event.group.id}\n"
        f"群名： {event.group.name}\n"
        f"群公告： {group_config.announcement}"
    )
    group_info = GroupInfo(
        group_id=str(event.group.id),  # 群号
        group_name=event.group.name,  # 群名
        group_announcement=group_config.announcement,  # 群公告
        ai_id=str(app.account),  # AI的QQ号
        ai_nickname=profile.nickname,  # AI昵称
        ai_age=str(profile.age),  # AI年龄
        ai_sex=profile.sex,  # AI性别
    )
    try:
        instance.chati.delete(session_id)
    except RuntimeError as e:
        pass
    try:
        reply = await utils.create_session_group_chati(session_id, group_info)
    except RuntimeError as e:
        await master_cor
        await utils.send_to_master(app, f"创建群组会话失败： {e}")
        return
    await master_cor
    try:
        await utils.send_group_message(app, event.group, reply.msg)
    except Exception as err:
        await utils.send_to_master(app, f"发送群组消息失败（{event.group.id}），已放弃: {str(err)}")
        return


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(app: Ariadne, event: GroupMessage):
    msg = event.message_chain.display
    if not msg.startswith("gpt "):
        if not At(app.account) in event.message_chain:
            return
        msg = event.message_chain.exclude(At).display
    else:
        msg = msg[4:]

    session_id = group_chati_session_id(app.account, event.sender.group.id)

    try:
        instance.chati.info(session_id)
    except RuntimeError as e:
        return

    try:
        reply = await utils.send_to_chati(msg, session_id)
    except RuntimeError as e:
        await utils.send_to_master(app, f"发送群组消息给 AI 失败： {e}")
        return
    message_chain = MessageChain([At(event.sender), reply.msg])
    try:
        await utils.send_group_message(app, event.sender.group, message_chain)
    except Exception as err:
        await utils.send_to_master(app, f"发送群组消息失败（{event.sender.id}），已放弃: {str(err)}")
        return
