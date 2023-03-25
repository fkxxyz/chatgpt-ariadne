from typing import Any

from flask import Flask
from graia.ariadne import Ariadne

from chati.chati import ChatI
from config import Config


class Instance:
    def __init__(self):
        self.app: Ariadne | None = None
        self.config: Config | None = None
        self.chati: ChatI | None = None
        self.app_server: Flask | None = None
        self.admin: Any | None = None


instance = Instance()
