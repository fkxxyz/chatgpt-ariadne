from typing import List

from graia.ariadne.message.element import Plain, Element

from app import instance
from middleware import MessageMiddleware


class SensitiveReplaceMiddleware(MessageMiddleware):
    def do(self, message: List[Element]) -> List[Element]:
        for i in range(len(message)):
            if isinstance(message[i], Plain):
                replaced, text = instance.sensitive.filter_1(str(message[i]))
                message[i] = Plain(text)
        return message
