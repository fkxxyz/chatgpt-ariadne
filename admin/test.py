from graia.ariadne import Ariadne
from graia.ariadne.message.element import Plain

import utils.message
from app import instance


async def on_master_test(app: Ariadne, text: str):
    message = [Plain(text)]
    exclude_set = instance.config.accounts_map[app.account].disabled_middlewares_map
    message = await instance.middlewares.execute_out(message, exclude_set)
    await utils.message.send_to_master(app, message)
