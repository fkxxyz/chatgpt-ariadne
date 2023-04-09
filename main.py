#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
import argparse
import json
import pkgutil
import threading
from typing import List

from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleBehaviour
from graia.broadcast import Broadcast
from graia.saya import Saya

import common
import middleware.sensitive_replace
import middleware.latex2text
import middleware.text2image
import utils.sensitive
from admin.index import Admin
from app import instance
from server import app as app_server
from chati.chati import ChatI
from config import Config


def main():
    parser = argparse.ArgumentParser(description="qq bot")
    parser.add_argument('--config', '-c', type=str, help='config json file', default=".test.config.json")
    args = parser.parse_args()

    # 读取配置文件
    config_ = Config.load(args.config)

    # 初始化全局对象
    chati = ChatI(config_.chati)
    instance.chati = chati
    instance.config = config_
    instance.sensitive = utils.sensitive.SensitiveFilter(config_.sensitive1, config_.sensitive2)
    instance.middlewares = common.MiddleWaresExecutor([
        middleware.latex2text.Latex2TextMiddleware(),
        middleware.text2image.Text2ImageMiddleware(),
        middleware.sensitive_replace.SensitiveReplaceMiddleware(),
    ])

    # 初始化 ariadne 对象
    bcc = create(Broadcast)
    saya = create(Saya)
    Ariadne.config(default_account=config_.accounts[0].account)
    for account_config in config_.accounts:
        Ariadne(connection=config(
            account_config.account,
            config_.verify_key,
            HttpClientConfig(host=config_.http),
            WebsocketClientConfig(host=config_.websocket),
        ))
    instance.app_server = app_server
    instance.admin = Admin()

    con = Console(broadcast=bcc, prompt="EroEroBot> ")
    saya.install_behaviours(ConsoleBehaviour(con))

    with saya.module_context():
        for module_info in pkgutil.iter_modules(["modules"]):
            if module_info.name.startswith("_"):
                # 假设模组是以 `_` 开头的，就不去导入
                # 根据 Python 标准，这类模组算是私有函数
                continue
            saya.require(f"modules.{module_info.name}")

    # 启动服务线程
    from waitress.server import create_server
    serv = create_server(
        app_server,
        host=config_.listen,
        port=config_.port,
        threads=256,
    )
    serv_thread = threading.Thread(target=serv.run)
    serv_thread.start()

    # 启动 Ariadne 应用程序
    Ariadne.launch_blocking()

    serv.close()
    serv_thread.join()


if __name__ == "__main__":
    exit(main())
