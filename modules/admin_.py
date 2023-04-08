from asyncio import Task
from typing import Optional

from graia.ariadne import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunched, ApplicationShutdowned
from graia.saya import Channel
from loguru import logger
from waitress.server import MultiSocketServer

from admin.error import TerminatedError
from app import instance

channel = Channel.current()

task: Optional[Task] = None
serv: MultiSocketServer | None = None


@Ariadne.broadcast.receiver(ApplicationLaunched)
async def start_admin_server():
    while True:
        session_id, request = await instance.admin.get_request()
        logger.info(f"收到请求（{request.seq}）: {session_id}")
        app_ = instance.app[request.account]
        try:
            if request.kwargs is None:
                result = await request.callable(app_, *request.args)
            else:
                result = await request.callable(app_, *request.args, **request.kwargs)
            instance.admin.set_result(session_id, result)
        except TerminatedError:
            break
        except Exception as err:
            logger.info(f"处理请求（{request.seq}）出错: {session_id}")
            instance.admin.set_result(session_id, None, err)


@Ariadne.broadcast.receiver(ApplicationShutdowned)
async def stop_admin_server():
    instance.admin.clear()
