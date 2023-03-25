import json
from dataclasses import dataclass

from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)

from config import Config

with open(".test.config.json", "r") as f:
    config_ = Config(**json.load(f))

# 读取配置文件
connection = config(
    config_.account,
    config_.verify_key,
    HttpClientConfig(host=config_.http),
    WebsocketClientConfig(host=config_.websocket),
)

app = Ariadne(connection)
