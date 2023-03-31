from asyncio import AbstractEventLoop, Task
from typing import Optional

from graia.ariadne import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunched, ApplicationShutdowned
from graia.ariadne.util.async_exec import io_bound
from graia.saya import Channel
from loguru import logger
from waitress.server import MultiSocketServer

from admin.error import TerminatedError
from app import instance

channel = Channel.current()

task: Optional[Task] = None
serv: MultiSocketServer | None = None


@io_bound
def admin_server():
    from waitress.server import create_server
    global serv
    serv = create_server(
        instance.app_server,
        host=instance.config.listen,
        port=instance.config.port,
        threads=256,
    )
    serv.run()


@instance.app.broadcast.receiver(ApplicationLaunched)
async def start_admin_server(app: Ariadne, loop: AbstractEventLoop):
    global task
    if not task:
        task = loop.create_task(admin_server())

    while True:
        session_id, request = await instance.admin.get_request()
        logger.info(f"收到请求（{request.seq}）: {session_id}")
        try:
            if request.kwargs is None:
                result = await request.callable(app, *request.args)
            else:
                result = await request.callable(app, *request.args, **request.kwargs)
            instance.admin.set_result(session_id, result)
        except TerminatedError:
            break
        except Exception as err:
            logger.info(f"处理请求（{request.seq}）出错: {session_id}")
            instance.admin.set_result(session_id, None, err)


@instance.app.broadcast.receiver(ApplicationShutdowned)
async def stop_admin_server():
    global task
    if task:
        instance.admin.clear()
        serv.close()
        await task
        task = None
