import abc
from typing import List

from graia.ariadne.message.element import Element


class MessageMiddleware(abc.ABC):
    @abc.abstractmethod
    async def do(self, message: List[Element]) -> List[Element]:
        raise NotImplementedError
