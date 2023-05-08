import io
from dataclasses import dataclass
from typing import List, Dict

import requests
from graia.ariadne.message.element import Element, Image, Plain
from graia.ariadne.util.async_exec import io_bound

from middleware import MessageMiddleware, MessageMiddlewareArguments


class OcrMiddleware(MessageMiddleware):
    def __init__(self, config: Dict):
        self.__url: str | None = config.get("url", None)

    async def do(self, message: List[Element], args: MessageMiddlewareArguments) -> List[Element]:
        if self.__url is None:
            return message
        for i in range(len(message)):
            if isinstance(message[i], Image):
                try:
                    image_bytes = await message[i].get_bytes()
                    tr_result: TrResult = await tr_ocr(self.__url, image_bytes)
                except Exception as err:
                    print(err)
                    import traceback
                    traceback.print_exc()
                    continue
                if tr_result.code != 200:
                    continue
                text_sum = ''
                for ocr_element in tr_result.data.raw_out:
                    text_sum += ocr_element.text + ' '
                message[i] = Plain('[图片:ocr:' + text_sum[:-1] + ']')
        return message


# https://github.com/alisen39/TrWebOCR/wiki/%E6%8E%A5%E5%8F%A3%E6%96%87%E6%A1%A3
@dataclass
class TrResultDataRawElement:
    position: List[List]
    text: str
    accuracy: float


@dataclass
class TrResultData:
    raw_out: List[TrResultDataRawElement]
    speed_time: float


@dataclass
class TrResult:
    code: int
    msg: str
    data: TrResultData


@io_bound
def tr_ocr(tr_url: str, image: bytes) -> TrResult:
    resp = requests.post(tr_url, files={"file": io.BytesIO(image)})
    resp.raise_for_status()
    tr_result = TrResult(**resp.json())
    if "img_detected" in tr_result.data:
        del tr_result.data["img_detected"]
    tr_result.data = TrResultData(**tr_result.data)

    raw_out = []
    for tr_result_data_raw_element in tr_result.data.raw_out:
        if type(tr_result_data_raw_element) != list:
            continue
        if len(tr_result_data_raw_element) != 3:
            continue
        assert type(tr_result_data_raw_element[0]) == list
        assert type(tr_result_data_raw_element[1]) == str
        assert type(tr_result_data_raw_element[2]) == float
        raw_out.append(TrResultDataRawElement(
            position=tr_result_data_raw_element[0],
            text=tr_result_data_raw_element[1][3:],
            accuracy=tr_result_data_raw_element[2],
        ))
    tr_result.data.raw_out = raw_out
    return tr_result
