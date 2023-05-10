import abc
import dataclasses
import json
import os.path
import typing


class JsonStorageInterface(abc.ABC):
    @abc.abstractmethod
    def __init__(self, path: str, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def save(self):
        raise NotImplementedError

    @staticmethod
    def load(path: str):
        raise NotImplementedError


def json_storage_class(cls):
    if not dataclasses.is_dataclass(cls):
        raise TypeError("dataclass_json_storage_class() should be called on dataclass types")

    class DataclassJsonStorage(cls, JsonStorageInterface):
        def __init__(self, path: str, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._path: str = path

        def save(self):
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            with open(os.path.join(self._path), "w") as f:
                f.write(json.dumps(dataclasses.asdict(self), indent=2))

        @staticmethod
        def load(path: str):
            try:
                with open(os.path.join(path), "r") as f:
                    config_json = json.load(f)
                json_storage = DataclassJsonStorage(path, **config_json)
            except (FileNotFoundError, json.JSONDecodeError):
                json_storage = DataclassJsonStorage(path)
                json_storage.save()
            return json_storage

    return DataclassJsonStorage


class DirectoryStorageInterface(abc.ABC):
    def __init__(self, path: str, *args, **kwargs):
        self._path = path

    @staticmethod
    def load(path: str):
        raise NotImplementedError


def directory_storage_class(cls):
    if not dataclasses.is_dataclass(cls):
        raise TypeError("config_directory_storage_class() should be called on dataclass instances")

    class ConfigStorage(cls, DirectoryStorageInterface):
        def __init__(self, path: str, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._path: str = path

        @staticmethod
        def load(path: str):
            d_class_dict = {}
            for key in cls.__annotations__:
                type_ = cls.__annotations__[key]
                if isinstance(type_, type):
                    if issubclass(type_, DirectoryStorageInterface):  # 文件夹嵌套
                        d_class_dict[key] = type_.load(os.path.join(path, key))
                    elif issubclass(type_, JsonStorageInterface):  # json 配置文件
                        d_class_dict[key] = type_.load(os.path.join(path, key + ".json"))
                elif typing.get_origin(type_) == dict:  # 文件夹配置字典
                    type_args = typing.get_args(type_)
                    assert len(type_args) == 2
                    assert type_args[0] == str
                    d_class_dict[key] = {}
                    try:
                        dir_content = os.listdir(os.path.join(path, key))
                    except FileNotFoundError:
                        os.makedirs(os.path.join(path, key), exist_ok=True)
                        dir_content = []
                    for element in dir_content:
                        if not os.path.isdir(os.path.join(path, key, element)):
                            continue
                        d_class_dict[key][element] = type_args[1].load(os.path.join(path, key, element))

            return ConfigStorage(path, **d_class_dict)

    return ConfigStorage
