import re
from typing import List, Callable

from graia.ariadne.message.element import Plain, Element

from middleware import MessageMiddleware


class Latex2Text:
    def __init__(self):
        from pylatexenc.latex2text import LatexNodes2Text
        self.latex_to_text = LatexNodes2Text().latex_to_text
        self.regex = re.compile(r'\$\$\n?(\\?[a-zA-Z0-9_]+.*)\n?\$\$|\$(\\?[a-zA-Z0-9_]+.*)\$')

    def replace(self, text: str) -> str:
        # 用 latex_to_text 函数替换所有匹配到的公式
        return self.regex.sub(lambda m: ' ' + self.latex_to_text(m.group(1) or m.group(2)) + ' ', text)


class Latex2TextMiddleware(MessageMiddleware):
    def __init__(self):
        self.replace: Callable[[str], str] = Latex2Text().replace

    async def do(self, message: List[Element]) -> List[Element]:
        for i in range(len(message)):
            if isinstance(message[i], Plain):
                text = str(message[i])
                if len(text) >= 192:
                    continue
                message[i] = Plain(self.replace(text))
        return message
