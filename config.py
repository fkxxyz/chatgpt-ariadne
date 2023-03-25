from dataclasses import dataclass


@dataclass
class Config:
    account: int
    verify_key: str
    http: str
    websocket: str
    chati: str
    masters: list[int]
    listen: str
    port: int
