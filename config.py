import json
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class AccountConfig:
    account: int
    masters: List[int]


@dataclass
class Config:
    accounts: List[AccountConfig]
    accounts_map: Dict[int, AccountConfig]
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
        config_json["accounts_map"] = {}
        for i in range(len(config_json["accounts"])):
            account_config = AccountConfig(**config_json["accounts"][i])
            config_json["accounts"][i] = account_config
            config_json["accounts_map"][account_config.account] = account_config
        config_ = Config(**config_json)
        return config_
