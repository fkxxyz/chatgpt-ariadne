from graia.ariadne.util.async_exec import io_bound

from app import instance
from chati.chati import SessionMessageResponse, UserInfo, GroupInfo


@io_bound
def send_to_chati(msg: str, session_id: str) -> SessionMessageResponse:
    instance.chati.send(msg, session_id)
    resp = instance.chati.get_until_end(session_id)
    return resp


@io_bound
def create_session_friend_chati(session_id: str, user_info: UserInfo) -> SessionMessageResponse:
    instance.chati.create_friend(session_id, user_info)
    resp = instance.chati.get_until_end(session_id)
    return resp


@io_bound
def create_session_group_chati(session_id: str, group_info: GroupInfo) -> SessionMessageResponse:
    instance.chati.create_group(session_id, group_info)
    resp = instance.chati.get_until_end(session_id)
    return resp


@io_bound
def inherit_session_friend_chati(session_id: str, user_info: UserInfo, memo: str,
                                 history: str) -> SessionMessageResponse:
    instance.chati.inherit_friend(session_id, user_info, memo, history)
    resp = instance.chati.get_until_end(session_id)
    return resp


@io_bound
def inherit_session_group_chati(session_id: str, group_info: GroupInfo, memo: str,
                                history: str) -> SessionMessageResponse:
    instance.chati.inherit_group(session_id, group_info, memo, history)
    resp = instance.chati.get_until_end(session_id)
    return resp
