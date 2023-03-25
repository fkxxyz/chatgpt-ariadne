import threading
from dataclasses import dataclass
from typing import Callable, Any, Dict

from admin.friend import *
from common import friend_chati_session_id


@dataclass
class AdminRequest:
    seq: int
    callable: Callable
    args: tuple = tuple()
    kwargs: dict = None

    replied: bool = False
    result: Any = None
    err: Any = None


class Admin:
    def __init__(self, self_id: int):
        self.__self_id = self_id
        self.__q: Dict[str, AdminRequest] = {}
        self.__lock = threading.Lock()
        self.__cond = threading.Condition(self.__lock)
        self.__terminated = False
        self.__seq = 0

    def clear(self):
        with self.__lock:
            self.__terminated = True
            self.__cond.notify_all()

    @io_bound
    def get_request(self) -> (str, AdminRequest):
        with self.__lock:
            while len(self.__q) == 0:
                self.__cond.wait()
                if self.__terminated:
                    raise error.TerminatedError
            session_id = next(iter(self.__q))
            return session_id, self.__q[session_id]

    def set_result(self, session_id: str, result: Any, err: Any = None):
        with self.__lock:
            assert session_id in self.__q
            self.__q[session_id].result = result
            self.__q[session_id].err = err
            self.__q[session_id].replied = True
            seq = self.__q[session_id].seq
            self.__cond.notify_all()
            while session_id in self.__q and self.__q[session_id].seq == seq:
                self.__cond.wait()
                if self.__terminated:
                    raise error.TerminatedError

    def __await_request(self, session_id: str, callable_: Callable, *args, **kwargs) -> Any:
        with self.__lock:
            while session_id in self.__q:
                self.__cond.wait()
                if self.__terminated:
                    raise error.TerminatedError
            self.__seq += 1
            self.__q[session_id] = AdminRequest(self.__seq, callable_, args, kwargs)
            self.__cond.notify_all()

            while self.__q[session_id].replied is False:
                self.__cond.wait()
                if self.__terminated:
                    raise error.TerminatedError
            result = self.__q[session_id].result
            err = self.__q[session_id].err
            del self.__q[session_id]
            self.__cond.notify_all()
        if err is not None:
            raise err
        return result

    def session_friend_create(self, user_id: int, comment: str, source: str) -> str:
        return self.__await_request(
            friend_chati_session_id(self.__self_id, user_id),
            on_session_friend_create, user_id, comment, source,
        )

    def session_friend_inherit(self, user_id: int, memo: str, history: str) -> None:
        return self.__await_request(
            friend_chati_session_id(self.__self_id, user_id),
            on_session_friend_inherit, user_id, memo, history,
        )

    def session_friend_send(self, user_id: int, msg: str) -> str:
        return self.__await_request(
            friend_chati_session_id(self.__self_id, user_id),
            on_session_friend_send, user_id, msg,
        )
