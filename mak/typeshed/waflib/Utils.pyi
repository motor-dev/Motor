import subprocess as subprocess
import os
import datetime

TimeoutExpired = subprocess.TimeoutExpired
from typing import Any, AnyStr, Callable, Dict, Iterable, List, Optional, Tuple, TypeVar, Union
from .ConfigSet import ConfigSet

SIG_NIL: bytes = ...
O644: int = ...
O755: int = ...

rot_chr: List[str] = ...
rot_idx: int = ...

is_win32: bool = ...


def readf(fname: str, m: str = ..., encoding: str = ...) -> AnyStr:
    ...


def writef(fname: str, data: AnyStr, m: str = ..., encoding: str = ...) -> None:
    ...


def h_file(fname: str) -> bytes:
    ...


def to_hex(s: str) -> bytes:
    ...


listdir = os.listdir


def num2ver(ver: Union[int, str, Tuple[int, ...]]) -> int:
    ...


def to_list(val: Union[str, List[str]]) -> List[str]:
    ...


def split_path(path: str) -> List[str]:
    ...


def check_dir(path: str) -> None:
    ...


def check_exe(name: str, env: Optional[ConfigSet] = ...) -> Optional[str]:
    ...


def quote_define_name(s: str) -> str:
    ...


def shell_escape(cmd: List[str]) -> str:
    ...


def h_list(lst: Iterable[Any]) -> bytes:
    ...


def h_fun(fun: Callable[..., Any]) -> bytes:
    ...


def h_cmd(ins: Any) -> bytes:
    ...


def subst_vars(expr: str, params: Union[Dict[str, Any], ConfigSet]) -> str:
    ...


def destos_to_binfmt(key: str) -> str:
    ...


def unversioned_sys_platform() -> str:
    ...


class Timer(object):

    def __init__(self) -> None:
        self.start_time: datetime.datetime = ...

    def __str__(self) -> str:
        ...

    def now(self) -> datetime.datetime:
        ...


F = TypeVar('F', bound=Callable[..., Any])


def run_once(fun: F) -> F:
    ...


def lib64() -> str:
    ...
