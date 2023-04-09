import json
from dataclasses import dataclass
from typing import List, Dict, Set


@dataclass
class AccountConfig:
    account: int
    masters: List[int]
    friend_type: str
    group_type: str
    disabled_middlewares: List[str] = None
    disabled_middlewares_map: Set[str] = None

    @staticmethod
    def from_dict(d: dict):
        account_config = AccountConfig(**d)
        if account_config.disabled_middlewares is None:
            account_config.disabled_middlewares = []
        account_config.disabled_middlewares_map = set(account_config.disabled_middlewares)
        return account_config


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
            account_config = AccountConfig.from_dict(config_json["accounts"][i])
            config_json["accounts"][i] = account_config
            config_json["accounts_map"][account_config.account] = account_config
        config_ = Config(**config_json)
        return config_
