from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)

from config import Config

config_ = Config.load(".test.config.json")

Ariadne.config(default_account=config_.accounts[0].account)
for account_config in config_.accounts:
    Ariadne.connection = config(
        account_config.account,
        config_.verify_key,
        HttpClientConfig(host=config_.http),
        WebsocketClientConfig(host=config_.websocket),
    )
    Ariadne.launch_blocking()
Ariadne.launch_blocking()
