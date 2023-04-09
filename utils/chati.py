from graia.ariadne.util.async_exec import io_bound

from app import instance
from chati.chati import SessionMessageResponse, UserInfo, GroupInfo


@io_bound
def send_to_chati(msg: str, session_id: str) -> str:
    instance.chati.send(msg, session_id)
    resp = instance.chati.get_until_end(session_id)
    return resp.msg


@io_bound
def create_session_friend_chati(session_id: str, type_: str, user_info: UserInfo) -> str:
    instance.chati.create_friend(session_id, type_, user_info)
    resp = instance.chati.get_until_end(session_id)
    return resp.msg


@io_bound
def create_session_group_chati(session_id: str, type_: str, group_info: GroupInfo) -> str:
    instance.chati.create_group(session_id, type_, group_info)
    resp = instance.chati.get_until_end(session_id)
    return resp.msg


@io_bound
def inherit_session_friend_chati(session_id: str, type_: str, user_info: UserInfo, memo: str,
                                 history: str) -> str:
    instance.chati.inherit_friend(session_id, type_, user_info, memo, history)
    resp = instance.chati.get_until_end(session_id)
    return resp.msg


@io_bound
def inherit_session_group_chati(session_id: str, type_: str, group_info: GroupInfo, memo: str,
                                history: str) -> str:
    instance.chati.inherit_group(session_id, type_, group_info, memo, history)
    resp = instance.chati.get_until_end(session_id)
    return resp.msg
