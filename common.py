from typing import List

from graia.amnesia.message import MessageChain

from middleware import MessageMiddleware


def friend_chati_session_id(self_id: int, supplicant: int) -> str:
    return f"qq-friend-{self_id}-{supplicant}"


def group_chati_session_id(self_id: int, supplicant: int) -> str:
    return f"qq-group-{self_id}-{supplicant}"


class MiddleWaresExecutor:
    def __init__(self, middlewares: List[MessageMiddleware]):
        self.middlewares: List[MessageMiddleware] = middlewares

    async def execute(self, message: MessageChain) -> MessageChain:
        for middleware in self.middlewares:
            message = await middleware.do(message)
        return message
