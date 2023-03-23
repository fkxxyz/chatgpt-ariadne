# 未读消息支持
# 为了防止重新部署时遗漏消息，使用单独进程来接收、缓存起来消息，供主进程使用

from typing import Iterable

from graia.ariadne.app import Ariadne
from graia.ariadne.connection import U_Info


def unread_queue(connection: Iterable[U_Info]):
    app = Ariadne(connection)
    assert False  # TODO: 实现未读消息支持
