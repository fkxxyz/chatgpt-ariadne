from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import BotJoinGroupEvent, BotInvitedJoinGroupRequestEvent, MemberJoinEvent
from graia.ariadne.message.element import At
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import utils
from app import instance
from chati.chati import GroupInfo
from common import group_chati_session_id

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def group_invite_listener(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    if event.supplicant in instance.config.masters:
        await event.accept()
    else:
        await event.reject()


@channel.use(ListenerSchema(listening_events=[BotJoinGroupEvent]))
async def group_add_listener(app: Ariadne, event: BotJoinGroupEvent):
    # 如果该群没有任何 master 成员群聊，则退群
    members = await app.get_member_list(event.group)
    members_set = {member.id for member in members}
    for master in instance.config.masters:
        if master in members_set:
            break
    else:
        await app.quit_group(event.group)
        return

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
        welcome_prompt="",
    )
    try:
        instance.chati.delete(session_id)
    except RuntimeError as e:
        pass
    try:
        reply = await utils.create_session_group_chati(session_id, group_info)
    except RuntimeError as e:
        await master_cor
        await utils.send_to_master(app, f"创建群组会话（{event.group.id}）失败： {e}")
        return
    await master_cor
    try:
        await utils.send_group_message(app, event.group, reply.msg)
    except Exception as err:
        await utils.send_to_master(app, f"发送群组消息失败（{event.group.id}），已放弃: {str(err)}")
        return


def generate_welcome_prompt(group_info: GroupInfo, member: Member) -> str:
    if len(group_info.welcome_prompt) == 0:
        return f"你已接入腾讯QQ平台，你的QQ号是{group_info.ai_id}，昵称是{group_info.ai_nickname}" \
               f"你正在一个群组里，群号是{group_info.group_id}，群名是{group_info.group_name}" \
               f"现在有一个新人入群了，QQ号是{member.id}，昵称是{member.name}" \
               f"请生成欢迎语（30个字以内）："
    else:
        prompt = group_info.welcome_prompt
        prompt = prompt.replace("{group_id}", group_info.group_id)
        prompt = prompt.replace("{group_name}", group_info.group_name)
        prompt = prompt.replace("{ai_id}", group_info.ai_id)
        prompt = prompt.replace("{ai_name}", group_info.ai_nickname)
        prompt = prompt.replace("{user_id}", str(member.id))
        prompt = prompt.replace("{user_name}", member.name)
        return prompt


@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def group_member_join_listener(app: Ariadne, event: MemberJoinEvent):
    session_id = group_chati_session_id(app.account, event.member.group.id)
    try:
        session_info = instance.chati.info(session_id)
    except RuntimeError as e:
        return
    group_info = GroupInfo(**session_info["params"])
    welcome_prompt = generate_welcome_prompt(group_info, event.member)
    try:
        reply = instance.chati.send_once(welcome_prompt)
    except RuntimeError as e:
        await utils.send_to_master(app, f"发送欢迎新人提示消息（{event.member.group.id}）给 AI 失败： {str(e)}")
        return
    message_chain = MessageChain([At(event.member), ' ' + reply])
    try:
        await utils.send_group_message(app, event.member.group, message_chain)
    except Exception as err:
        await utils.send_to_master(app, f"发送群组消息失败（{event.member.group.id}），已放弃: {str(err)}")
        return


busy_group = set()


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

    if event.sender.group.id in busy_group:
        await utils.send_group_message(app, event.sender.group, MessageChain([At(event.sender), ' 消息太快啦，稍等一下吧']))
        return

    busy_group.add(event.sender.group.id)
    try:
        reply = await utils.send_to_chati(msg, session_id)
    except RuntimeError as e:
        await utils.send_to_master(app, f"发送群组消息（{event.sender.group.id}）给 AI 失败： {str(e)}")
        await utils.send_group_message(app, event.sender.group,
                                       MessageChain([At(event.sender), f' 抱歉，我服务器似乎出了点问题： {str(e)}']))
        return
    finally:
        busy_group.remove(event.sender.group.id)
    message_chain = MessageChain([At(event.sender), ' ' + reply.msg])
    try:
        await utils.send_group_message(app, event.sender.group, message_chain)
    except Exception as err:
        await utils.send_to_master(app, f"发送群组消息失败（{event.sender.group.id}），已放弃: {str(err)}")
        return
