import re
from typing import List

from graia.ariadne.message.element import Plain, Element

from middleware import MessageMiddleware


class Latex2TextMiddleware(MessageMiddleware):
    def __init__(self):
        from pylatexenc.latex2text import LatexNodes2Text
        self.latex_to_text = LatexNodes2Text().latex_to_text
        self.regex = re.compile(r'\$\$(.*?)\$\$|\$(.*?)\$')

    def do(self, message: List[Element]) -> List[Element]:
        for i in range(len(message)):
            if isinstance(message[i], Plain):
                message[i] = Plain(self.replace(str(message[i])))
        return message

    def replace(self, text: str) -> str:
        # 用 latex_to_text 函数替换所有匹配到的公式
        return self.regex.sub(lambda m: self.latex_to_text(m.group(1) or m.group(2)), text)

