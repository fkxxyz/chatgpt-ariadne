import http

import requests
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import BotJoinGroupEvent, BotInvitedJoinGroupRequestEvent, MemberJoinEvent
from graia.ariadne.message.element import At, Plain
from graia.ariadne.model import Member, Profile
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import utils.message
import utils.chati
from app import instance
from chati.chati import GroupInfo
from common import group_chati_session_id
from middleware import MessageMiddlewareArguments

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def group_invite_listener(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    if event.supplicant in instance.config.accounts_map[app.account].masters:
        await event.accept()
    else:
        await event.reject()


@channel.use(ListenerSchema(listening_events=[BotJoinGroupEvent]))
async def group_add_listener(app: Ariadne, event: BotJoinGroupEvent):
    # 如果该群没有任何 master 成员群聊，则退群
    members = await app.get_member_list(event.group)
    members_set = {member.id for member in members}
    for master in instance.config.accounts_map[app.account].masters:
        if master in members_set:
            break
    else:
        await app.quit_group(event.group)
        return

    session_id = group_chati_session_id(app.account, event.group.id)
    group_config = await app.get_group_config(event.group)
    profile = await app.get_bot_profile()
    master_cor = utils.message.send_to_master(
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
    except requests.HTTPError as e:
        pass
    try:
        type_ = instance.config.accounts_map[app.account].group_type
        reply = await utils.chati.create_session_group_chati(session_id, type_, group_info)
    except requests.HTTPError as e:
        await master_cor
        await utils.message.send_to_master(app, f"创建群组会话（{event.group.id}）失败： {e}")
        return
    await master_cor
    try:
        await utils.message.send_group_message(app, event.group, reply)
    except Exception as err:
        await utils.message.send_to_master(app, f"发送群组消息失败（{event.group.id}），已放弃: {str(err)}")
        return


def generate_welcome_prompt(group_info: GroupInfo, member: Member, profile: Profile) -> str:
    if len(group_info.welcome_prompt) == 0:
        return f"你已接入腾讯QQ平台，你的QQ号是{group_info.ai_id}，昵称是{group_info.ai_nickname}" \
               f"你正在一个群组里，群号是{group_info.group_id}，群名是{group_info.group_name}" \
               f"现在有一个新人入群了，QQ号是{member.id}，昵称是{member.name}，年龄{profile.age}，性别{profile.sex}" \
               f"请生成欢迎语（30个字以内）："
    else:
        prompt = group_info.welcome_prompt
        prompt = prompt.replace("{group_id}", group_info.group_id)
        prompt = prompt.replace("{group_name}", group_info.group_name)
        prompt = prompt.replace("{ai_id}", group_info.ai_id)
        prompt = prompt.replace("{ai_name}", group_info.ai_nickname)
        prompt = prompt.replace("{user_id}", str(member.id))
        prompt = prompt.replace("{user_name}", member.name)
        prompt = prompt.replace("{user_age}", str(profile.age))
        prompt = prompt.replace("{user_sex}", profile.sex)
        return prompt


@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def group_member_join_listener(app: Ariadne, event: MemberJoinEvent):
    session_id = group_chati_session_id(app.account, event.member.group.id)
    try:
        session_info = instance.chati.info(session_id)
    except requests.HTTPError as e:
        return
    group_info = GroupInfo(**session_info["params"])
    profile = await app.get_member_profile(event.member)
    welcome_prompt = generate_welcome_prompt(group_info, event.member, profile)
    try:
        reply = instance.chati.send_once(welcome_prompt)
    except requests.HTTPError as e:
        await utils.message.send_to_master(app, f"发送欢迎新人提示消息（{event.member.group.id}）给 AI 失败： {str(e)}")
        return
    message_chain = MessageChain([At(event.member), ' ' + reply])
    try:
        await utils.message.send_group_message(app, event.member.group, message_chain)
    except Exception as err:
        await utils.message.send_to_master(app, f"发送群组消息失败（{event.member.group.id}），已放弃: {str(err)}")
        return


busy_group = set()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(app: Ariadne, event: GroupMessage):
    if event.sender.id == 2854196310:  # 忽略Q群管家
        return
    msg = event.message_chain.display
    if not msg.startswith("gpt "):
        if not At(app.account) in event.message_chain:
            return
        msg = event.message_chain.exclude(At).display
    else:
        msg = msg[4:]
    if len(msg) == 0:
        msg = " "

    session_id = group_chati_session_id(app.account, event.sender.group.id)

    try:
        instance.chati.info(session_id)
    except requests.HTTPError as e:
        return

    if session_id in busy_group:
        await utils.message.send_group_message(app, event.sender.group,
                                               MessageChain([At(event.sender), Plain(" 我还在思考中，请稍等...")]))
        return

    busy_group.add(session_id)
    try:
        reply = await utils.chati.send_to_chati(msg, session_id)
    except requests.HTTPError as e:
        if e.response.status_code == http.HTTPStatus.REQUEST_ENTITY_TOO_LARGE:
            await utils.message.send_group_message(
                app, event.sender.group,
                MessageChain([At(event.sender), Plain(f' 抱歉，消息太长啦，我无法接收')])
            )
        else:
            err_str = f"发送群组消息（{event.sender.id}）给 AI 失败： {str(e)} - {e.response.content.decode()}"
            await utils.message.send_to_master(app, err_str)
            err_str = f'抱歉，我服务器似乎出了点问题： 响应返回错误 {e.response.status_code}： {e.response.content.decode()}'
            await utils.message.send_group_message(
                app, event.sender.group, MessageChain([At(event.sender), Plain(err_str)]))
        return
    finally:
        busy_group.remove(session_id)
    exclude_set = instance.config.accounts_map[app.account].disabled_middlewares_map
    message = [At(event.sender), Plain(' ' + reply)]
    message = await instance.middlewares.execute(message, exclude_set)
    try:
        active_message = await utils.message.send_group_message(app, event.sender.group, MessageChain(message))
    except Exception as err:
        await utils.message.send_to_master(app, f"发送群组消息失败（{event.sender.group.id}），已放弃: {str(err)}")
        return

    if active_message.id <= 0:
        await utils.message.send_to_master(app, f"发送群组消息无效（{event.sender.group.id}），准备转换成图片重试")

        message = [At(event.sender), Plain(' ' + reply)]
        message = await instance.middlewares.execute(message, exclude_set, MessageMiddlewareArguments(
            force_image=True,
        ))
        await utils.message.send_to_master(app, MessageChain(message))
        try:
            active_message = await utils.message.send_group_message(app, event.sender.group, MessageChain(message))
        except Exception as err:
            await utils.message.send_to_master(app, f"发送群组消息失败（{event.sender.group.id}），已放弃: {str(err)}")
            return
        if active_message.id <= 0:
            await utils.message.send_to_master(app, f"发送群组消息无效（{event.sender.group.id}），并且已转换成图片，已放弃")
            return
        return
