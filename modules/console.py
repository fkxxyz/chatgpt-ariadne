from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleSchema
from graia.ariadne.message.parser.twilight import MatchResult, Twilight
from graia.saya import Channel

from utils.message import send_to_master

channel = Channel.current()


@channel.use(ConsoleSchema([Twilight.from_command("master {message}")]))
async def on_send_to_master(app: Ariadne, message: MatchResult):
    await send_to_master(app, message.result.display)


@channel.use(ConsoleSchema([Twilight.from_command("exit")]))
async def on_exit(app: Ariadne, console: Console):
    app.stop()
    console.stop()
