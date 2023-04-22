import asyncio
import http
import time

import requests
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.event.mirai import NewFriendRequestEvent
from graia.ariadne.message.element import Plain

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import utils.message
import utils.chati
from app import instance
from chati.chati import UserInfo
from common import friend_chati_session_id
from middleware import MessageMiddlewareArguments

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[NewFriendRequestEvent]))
async def new_friend_request_listener(app: Ariadne, event: NewFriendRequestEvent):
    session_id = friend_chati_session_id(app.account, event.supplicant)
    profile = await app.get_bot_profile()
    master_cor = utils.message.send_to_master(
        app,
        f"我收到好友申请\n"
        f"QQ： {event.supplicant}\n"
        f"昵称： {event.nickname}\n"
        f"附加消息： {event.message}"
    )
    await master_cor
    return
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
        await utils.chati.delete(session_id)
    except requests.HTTPError as e:
        pass
    try:
        type_ = instance.config.accounts_map[app.account].friend_type
        reply = await utils.chati.create_session_friend_chati(session_id, type_, user_info)
    except requests.HTTPError as e:
        await master_cor
        await utils.message.send_to_master(app, f"创建好友会话（{event.supplicant}）失败： {e}")
        return
    await master_cor
    await event.accept()
    time.sleep(2)
    friend = await app.get_friend(event.supplicant)
    if friend is None:
        # 获取好友失败
        await utils.message.send_to_master(app, f"获取好友失败（{event.supplicant}）")
        return
    try:
        await utils.message.send_friend_message(app, friend, MessageChain([Plain(reply)]))
    except Exception as err:
        await utils.message.send_to_master(app, f"发送好友消息失败（{event.supplicant}），已放弃: {str(err)}")
        return
    await utils.message.send_to_master(app, f"已成功同意好友申请（{event.supplicant}）")


busy_friend = set()


@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def friend_message_listener(app: Ariadne, event: FriendMessage):
    # 忽略自己
    if event.sender.id == app.account:
        return

    session_id = friend_chati_session_id(app.account, event.sender.id)

    if session_id in busy_friend:
        await utils.message.send_friend_message(app, event.sender, MessageChain([Plain("我还在思考中，请稍等...")]))
        return

    busy_friend.add(session_id)

    try:
        chati_task = asyncio.ensure_future(utils.chati.send_to_chati(event.message_chain.display, session_id))
        try:
            reply = await asyncio.wait_for(asyncio.shield(chati_task), timeout=30)
        except asyncio.TimeoutError:
            await utils.message.send_friend_message(
                app, event.sender,
                MessageChain([Plain("非常抱歉，长时间没有回应，我的服务器可能出了点问题，请稍等...")])
            )
            await utils.message.send_to_master(app, f"发送好友消息（{event.sender.id}）给 AI 超时")

            # 继续等待
            await chati_task
            reply = chati_task.result()
    except requests.HTTPError as e:
        if e.response.status_code == http.HTTPStatus.REQUEST_ENTITY_TOO_LARGE:
            await utils.message.send_friend_message(
                app, event.sender,
                MessageChain([Plain(f'抱歉，消息太长啦，我无法接收')])
            )
        else:
            err_str = f"发送好友消息（{event.sender.id}）给 AI 失败： {str(e)} - {e.response.content.decode()}"
            await utils.message.send_to_master(app, err_str)
            err_str = f'抱歉，我服务器似乎出了点问题： 响应返回错误 {e.response.status_code}： {e.response.content.decode()}'
            await utils.message.send_friend_message(app, event.sender, MessageChain([Plain(err_str)]))
        return
    except Exception as e:
        import traceback
        traceback.print_exc()

        err_str = f"发送好友消息（{event.sender.id}）给 AI 失败： {str(e)}"
        await utils.message.send_to_master(app, err_str)
        err_str = f'抱歉，我服务器似乎出了点问题： {str(e)}'
        await utils.message.send_friend_message(app, event.sender, MessageChain([Plain(err_str)]))
        return
    finally:
        busy_friend.remove(session_id)
    exclude_set = instance.config.accounts_map[app.account].disabled_middlewares_map
    message = [Plain(reply)]
    message = await instance.middlewares.execute(message, exclude_set)
    try:
        active_message = await utils.message.send_friend_message(app, event.sender, MessageChain(message))
    except Exception as err:
        await utils.message.send_to_master(app, f"发送好友消息失败（{event.sender.id}），已放弃: {str(err)}")
        return

    if active_message.id <= 0:
        await utils.message.send_to_master(app, f"发送好友消息无效（{event.sender.id}），准备转换成图片重试")

        message = [Plain(reply)]
        message = await instance.middlewares.execute(message, exclude_set, MessageMiddlewareArguments(
            force_image=True,
        ))
        await utils.message.send_to_master(app, MessageChain(message))
        try:
            active_message = await utils.message.send_friend_message(app, event.sender, MessageChain(message))
        except Exception as err:
            await utils.message.send_to_master(app, f"发送好友消息失败（{event.sender.id}），已放弃: {str(err)}")
            return
        if active_message.id <= 0:
            await utils.message.send_to_master(app, f"发送好友消息无效（{event.sender.id}），并且已转换成图片，已放弃")
            return
        return
