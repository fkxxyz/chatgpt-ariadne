from chati.chati import ChatI
from config import Config


class Instance:
    def __init__(self):
        self.config: Config | None = None
        self.chati: ChatI | None = None


instance = Instance()
