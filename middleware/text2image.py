import base64
import tempfile
from io import BytesIO
from typing import List, Coroutine

import PIL.Image
import imgkit
import qrcode
import requests
from graia.ariadne.message.element import Element, Plain, Image

import markdown
from graia.ariadne.util.async_exec import io_bound
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.tables import TableExtension
from mdx_math import MathExtension

from middleware import MessageMiddleware


class Text2ImageMiddleware(MessageMiddleware):
    async def do(self, message: List[Element]) -> List[Element]:
        for i in range(len(message)):
            if isinstance(message[i], Plain):
                text = str(message[i])
                if len(text) >= 192:
                    image_data = await text2image(text)
                    message[i] = Image(data_bytes=image_data)
        return message


@io_bound
def text2qrcode(text: str) -> bytes:
    data = {
        'expires': '86400',
        'format': 'url',
        'lexer': '_markdown',
        'content': text,
    }
    try:
        with requests.post(
                'https://pastebin.mozilla.org/api/',
                data=data
        ) as resp:
            resp.raise_for_status()
            url = resp.text.strip()
    except Exception as e:
        url = "上传失败：" + str(e)
    image = qrcode.make(url)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return buffered.getvalue()


@io_bound
def html2image(html_str: str) -> bytes:
    # 将 html 转换为图片
    temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=True)
    imgkit.from_string(html_str, temp_png.name, options={
        'format': 'png',
        'width': 360,
    })
    image = PIL.Image.open(temp_png.file)

    # 将 png 图片优化
    buffered = BytesIO()
    image.save(buffered, format="PNG", optimize=True)
    del temp_png

    return buffered.getvalue()


async def text2image(text: str) -> bytes:
    # 将文本上传生成二维码
    cor_text2qrcode: Coroutine = text2qrcode(text)

    # 将 markdown 文本转换为 html
    text = text.replace("\n", "  \n")
    extensions = [
        MathExtension(enable_dollar_delimiter=True),
        CodeHiliteExtension(linenums=False, css_class='highlight', noclasses=False, guess_lang=True),
        TableExtension(),
        'fenced_code'
    ]
    md = markdown.Markdown(extensions=extensions)
    html_content_str = md.convert(text)

    # 将得到的二维码转换成 base64
    qrcode_data = await cor_text2qrcode
    qrcode_base64_data = "data:image/jpeg;base64," + base64.b64encode(qrcode_data).decode('utf-8')

    html_str = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
    font-family: "Custom Font","Microsoft Yahei",Helvetica,arial,sans-serif;
    font-size: 30px;
    line-height: 1.6;
    padding-top: 10px;
    padding-bottom: 10px;
    background-color: #e8fbf1;
    padding: 30px;
    color: #516272
}}
</style>
</head>
<body>
{html_content_str}
<img src="{qrcode_base64_data}" style="float:right; width:120px; height:120px;" />
</body>
</html>"""

    # 将 html 转换为图片
    image_data = await html2image(html_str)
    return image_data
