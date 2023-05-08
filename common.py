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
    def __init__(self, config_: Dict[str, Dict]):
        self.middlewares_in_map: Dict[str, MessageMiddleware] = {}
        for middleware_name in middleware.index.default_middlewares_in:
            m_config = config_.get(middleware_name, {})
            m = middleware.index.middlewares_in[middleware_name](m_config)
            self.middlewares_in_map[middleware_name] = m

        self.middlewares_out_map: Dict[str, MessageMiddleware] = {}
        for middleware_name in middleware.index.default_middlewares_out:
            m_config = config_.get(middleware_name, {})
            m = middleware.index.middlewares_out[middleware_name](m_config)
            self.middlewares_out_map[middleware_name] = m

    async def execute_in(self, message: MessageChain, exclude_set: Set[str],
                         args: MessageMiddlewareArguments = None) -> MessageChain:
        if args is None:
            args = MessageMiddlewareArguments()
        for middleware_name in middleware.index.default_middlewares_in:
            if middleware_name in exclude_set:
                continue
            message = await self.middlewares_in_map[middleware_name].do(message, args)
        return message

    async def execute_out(self, message: MessageChain, exclude_set: Set[str],
                          args: MessageMiddlewareArguments = None) -> MessageChain:
        if args is None:
            args = MessageMiddlewareArguments()
        for middleware_name in middleware.index.default_middlewares_out:
            if middleware_name in exclude_set:
                continue
            message = await self.middlewares_out_map[middleware_name].do(message, args)
        return message
