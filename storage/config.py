import abc
from dataclasses import dataclass
from typing import Dict

from storage.storage import json_storage_class, JsonStorageInterface, DirectoryStorageInterface, \
    directory_storage_class


@json_storage_class
@dataclass
class AccountGlobalConfig(JsonStorageInterface, abc.ABC):
    friend_enabled: bool = False  # 帐号全局私聊启用开关
    group_enabled: bool = False  # 帐号全局群聊启用开关


@directory_storage_class
@dataclass
class AccountConfigDirectory(DirectoryStorageInterface, abc.ABC):
    g: AccountGlobalConfig


@json_storage_class
@dataclass
class GlobalConfig(JsonStorageInterface, abc.ABC):
    enabled: bool = False  # 所有帐号的启用开关


@directory_storage_class
@dataclass
class GlobalConfigDirectory(DirectoryStorageInterface, abc.ABC):
    g: GlobalConfig
    accounts: Dict[str, AccountConfigDirectory]

    def new_account(self, account_name) -> AccountConfigDirectory:
        account = AccountConfigDirectory.load(f"global/accounts/{account_name}")
        self.accounts[account_name] = account
        return account
