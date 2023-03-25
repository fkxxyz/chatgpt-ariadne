from graia.ariadne import Ariadne

from app import instance


async def send_to_master(app: Ariadne, msg: str):
    for master in instance.config.master:
        try:
            friend = await app.get_friend(master, assertion=True, cache=True)
        except ValueError:
            continue
        await app.send_message(friend, msg)
