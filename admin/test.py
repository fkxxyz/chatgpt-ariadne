from graia.ariadne import Ariadne
from graia.ariadne.message.element import Plain

import utils.message
from app import instance


async def on_master_test(app: Ariadne, text: str):
    message = [Plain(text)]
    message = await instance.middlewares.execute(message)
    await utils.message.send_to_master(app, message)
