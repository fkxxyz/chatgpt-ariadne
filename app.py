from typing import Any, Dict

from flask import Flask
from graia.ariadne import Ariadne

import common
import utils.sensitive
from chati.chati import ChatI
from config import Config


class Instance:
    def __init__(self):
        self.app: Dict[int, Ariadne] = {}
        self.config: Config | None = None
        self.chati: ChatI | None = None
        self.app_server: Flask | None = None
        self.admin: Any | None = None
        self.sensitive: utils.sensitive.SensitiveFilter | None = None
        self.middlewares: common.MiddleWaresExecutor | None = None


instance = Instance()
