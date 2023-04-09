from typing import List, Set, Dict

from graia.amnesia.message import MessageChain

import middleware.index
from middleware import MessageMiddleware


def friend_chati_session_id(self_id: int, supplicant: int) -> str:
    return f"qq-friend-{self_id}-{supplicant}"


def group_chati_session_id(self_id: int, supplicant: int) -> str:
    return f"qq-group-{self_id}-{supplicant}"


class MiddleWaresExecutor:
    def __init__(self):
        self.middlewares_map: Dict[str, MessageMiddleware] = {}
        for middleware_name in middleware.index.default_middlewares:
            m = middleware.index.middlewares[middleware_name]()
            self.middlewares_map[middleware_name] = m

    async def execute(self, message: MessageChain, exclude_set: Set[str]) -> MessageChain:
        for middleware_name in middleware.index.default_middlewares:
            if middleware_name in exclude_set:
                continue
            message = await self.middlewares_map[middleware_name].do(message)
        return message
