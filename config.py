import json
from dataclasses import dataclass
from typing import List


@dataclass
class AccountConfig:
    account: int
    masters: List[int]


@dataclass
class Config:
    accounts: List[AccountConfig]
    verify_key: str
    http: str
    websocket: str
    chati: str
    listen: str
    port: int
    sensitive1: str
    sensitive2: str

    @staticmethod
    def load(path_: str):
        with open(path_, "r") as f:
            config_json = json.load(f)
        for i in range(len(config_json["accounts"])):
            config_json["accounts"][i] = AccountConfig(**config_json["accounts"][i])
        config_ = Config(**config_json)
        return config_
