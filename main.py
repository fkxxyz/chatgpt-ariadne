#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
import argparse
import json
import pkgutil

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

from admin.index import Admin
from app import instance
from server import app as app_server
from chati.chati import ChatI
from config import Config


def main():
    parser = argparse.ArgumentParser(description="qq bot")
    parser.add_argument('--config', '-c', type=str, help='config json file', default=".test.config.json")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config_ = Config(**json.load(f))

    # 初始化全局对象
    chati = ChatI(config_.chati)
    instance.chati = chati
    instance.config = config_

    # 读取配置文件
    connection = config(
        config_.account,
        config_.verify_key,
        HttpClientConfig(host=config_.http),
        WebsocketClientConfig(host=config_.websocket),
    )

    bcc = create(Broadcast)
    saya = create(Saya)
    app = Ariadne(connection)
    instance.app = app
    instance.app_server = app_server
    instance.admin = Admin(config_.account)

    con = Console(broadcast=bcc, prompt="EroEroBot> ")
    saya.install_behaviours(ConsoleBehaviour(con))

    with saya.module_context():
        for module_info in pkgutil.iter_modules(["modules"]):
            if module_info.name.startswith("_"):
                # 假设模组是以 `_` 开头的，就不去导入
                # 根据 Python 标准，这类模组算是私有函数
                continue
            saya.require(f"modules.{module_info.name}")

    Ariadne.launch_blocking()


if __name__ == "__main__":
    exit(main())
