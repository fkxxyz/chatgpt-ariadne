import http
import json
import time
from typing import Callable

import requests
from dataclasses import dataclass, asdict

from loguru import logger


@dataclass
class UserInfo:
    user_id: str  # 用户QQ号
    user_nickname: str  # 用户昵称
    user_age: str  # 用户年龄
    user_sex: str  # 用户性别
    ai_id: str  # AI的QQ号
    ai_nickname: str  # AI昵称
    ai_age: str  # AI年龄
    ai_sex: str  # AI性别
    add_source: str  # 加好友时的来源
    add_comment: str  # 加好友时的附加消息
    level: int = 1  # chati 等级


@dataclass
class GroupInfo:
    group_id: str  # 群号
    group_name: str  # 群名
    group_announcement: str  # 群公告
    ai_id: str  # AI的QQ号
    ai_nickname: str  # AI昵称
    ai_age: str  # AI年龄
    ai_sex: str  # AI性别
    level: int = 65536  # chati 等级


def call_until_success(fn: Callable[[], requests.Response]) -> bytes:
    while True:
        try:
            resp = fn()
        except requests.RequestException as e:
            logger.info(f"请求错误： {e}")
            logger.info(f"等待 10 秒后重试 ...")
            time.sleep(10)
            continue
        if resp.status_code % 100 == 5:
            logger.info(f"响应返回错误 {resp.status_code}： {resp.content.decode()}")
            logger.info(f"等待 10 秒后重试 ...")
            time.sleep(10)
            continue
        if resp.status_code != http.HTTPStatus.OK:
            logger.info(f"响应返回错误 {resp.status_code} ，终止： {resp.content.decode()}")
            raise RuntimeError(f"响应返回错误 {resp.status_code}： {resp.content.decode()}")

        return resp.content


@dataclass
class ChatISessionInfo:
    id: str
    type: str
    params: dict


@dataclass
class SessionMessageResponse:
    mid: str
    msg: str
    end: bool


class ChatI:
    def __init__(self, url: str):
        self.__url = url
        self.__session = requests.Session()

    def create(self, id_: str, type_: str, params: dict) -> ChatISessionInfo:
        data = params
        params = {'id': id_, 'type': type_}
        content = call_until_success(lambda: self.__session.put(f"{self.__url}/api/create", params=params, json=data))
        content_dict = json.loads(content)
        return ChatISessionInfo(**content_dict)

    def inherit(self, id_: str, type_: str, params: dict, memo: str, history: str) -> ChatISessionInfo:
        params_ = {'id': id_, 'type': type_}
        data = {
            'params': params,
            'memo': memo,
            'history': history
        }
        content = call_until_success(lambda: self.__session.put(f"{self.__url}/api/inherit", params=params_, json=data))
        content_dict = json.loads(content)
        return ChatISessionInfo(**content_dict)

    def delete(self, id_: str):
        params = {'id': id_}
        call_until_success(lambda: self.__session.delete(f"{self.__url}/api/delete", params=params))

    def send(self, msg: str, id_: str):
        data = {'message': msg}
        params = {'id': id_}
        content = call_until_success(lambda: self.__session.post(f"{self.__url}/api/send", params=params, json=data))
        content_dict = json.loads(content)
        return content_dict

    def get(self, id_: str) -> SessionMessageResponse:
        params = {'id': id_}
        content = call_until_success(lambda: self.__session.get(f"{self.__url}/api/get", params=params))
        content_dict = json.loads(content)
        return SessionMessageResponse(**content_dict)

    def get_until_end(self, id_: str) -> SessionMessageResponse:
        while True:
            resp = self.get(id_)
            if resp.end:
                return resp
            time.sleep(0.5)

    def create_friend(self, id_: str, user_info: UserInfo) -> ChatISessionInfo:
        params = asdict(user_info)
        return self.create(id_, "qq-friend", params)

    def inherit_friend(self, id_: str, user_info: UserInfo, memo: str, history: str) -> ChatISessionInfo:
        params = asdict(user_info)
        return self.inherit(id_, "qq-friend", params, memo, history)

    def create_group(self, id_: str, group_info: GroupInfo) -> ChatISessionInfo:
        params = asdict(group_info)
        return self.create(id_, "qq-group", params)

    def inherit_group(self, id_: str, group_info: GroupInfo, memo: str, history: str) -> ChatISessionInfo:
        params = asdict(group_info)
        return self.inherit(id_, "qq-group", params, memo, history)
