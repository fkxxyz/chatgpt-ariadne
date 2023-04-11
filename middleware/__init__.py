import abc
from typing import List

from graia.ariadne.message.element import Element

from middleware.common import MessageMiddlewareArguments


class MessageMiddleware(abc.ABC):
    @abc.abstractmethod
    async def do(self, message: List[Element], args: MessageMiddlewareArguments) -> List[Element]:
        raise NotImplementedError
