from typing import List, Set, Dict

from graia.amnesia.message import MessageChain

import middleware.index
from middleware import MessageMiddleware
from middleware.common import MessageMiddlewareArguments


def friend_chati_session_id(self_id: int, supplicant: int) -> str:
    return f"qq-friend-{self_id}-{supplicant}"


def group_chati_session_id(self_id: int, supplicant: int) -> str:
    return f"qq-group-{self_id}-{supplicant}"


def group_member_chati_session_id(self_id: int, supplicant: int, member: int) -> str:
    return f"qq-group-member-{self_id}-{supplicant}-{member}"


class MiddleWaresExecutor:
    def __init__(self):
        self.middlewares_map: Dict[str, MessageMiddleware] = {}
        for middleware_name in middleware.index.default_middlewares:
            m = middleware.index.middlewares[middleware_name]()
            self.middlewares_map[middleware_name] = m

    async def execute(self, message: MessageChain, exclude_set: Set[str],
                      args: MessageMiddlewareArguments = None) -> MessageChain:
        if args is None:
            args = MessageMiddlewareArguments()
        for middleware_name in middleware.index.default_middlewares:
            if middleware_name in exclude_set:
                continue
            message = await self.middlewares_map[middleware_name].do(message, args)
        return message
