from graia.ariadne import Ariadne
from graia.ariadne.util.async_exec import io_bound

from app import instance
from chati.chati import SessionMessageResponse, UserInfo


async def send_to_master(app: Ariadne, msg: str):
    for master in instance.config.masters:
        try:
            friend = await app.get_friend(master, assertion=True, cache=True)
        except ValueError:
            continue
        await app.send_message(friend, msg)


@io_bound
def send_to_chati(msg: str, session_id: str) -> SessionMessageResponse:
    instance.chati.send(msg, session_id)
    resp = instance.chati.get_until_end(session_id)
    return resp


@io_bound
def create_session_chati(session_id: str, user_info: UserInfo) -> SessionMessageResponse:
    instance.chati.create_friend(session_id, user_info)
    resp = instance.chati.get_until_end(session_id)
    return resp


@io_bound
def inherit_session_chati(session_id: str, user_info: UserInfo, memo: str, history: str) -> SessionMessageResponse:
    instance.chati.inherit_friend(session_id, user_info, memo, history)
    resp = instance.chati.get_until_end(session_id)
    return resp
