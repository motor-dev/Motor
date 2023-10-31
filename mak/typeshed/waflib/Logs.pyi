import logging
from typing import Any, Dict, List, Optional, TextIO, Union

LOG_FORMAT: str = ...
HOUR_FORMAT: str = ...

zones: List[str] = ...
verbose: int = ...

colors_lst: Dict[str, Union[bool, str]] = ...

indicator: str = ...


def enable_colors(use: int) -> None:
    ...


def get_term_cols() -> int:
    ...


def get_color(cl: str) -> str:
    ...


class color_dict(object):

    def __getattr__(self, a: str) -> str:
        ...

    def __call__(self, a: str) -> str:
        ...


colors: color_dict = ...


class log_filter(logging.Filter):

    def __init__(self, name: str = ...):
        logging.Filter.__init__(self, name)

    def filter(self, rec: logging.LogRecord) -> bool:
        ...


class log_handler(logging.StreamHandler[TextIO]):

    def emit(self, record: logging.LogRecord) -> None:
        ...

    def emit_override(self, record: logging.LogRecord, **kw: Any) -> None:
        ...


class formatter(logging.Formatter):

    def __init__(self) -> None:
        logging.Formatter.__init__(self, LOG_FORMAT, HOUR_FORMAT)

    def format(self, rec: logging.LogRecord) -> str:
        ...


log: logging.Logger = ...


def debug(msg: str, **kw: Any) -> None:
    ...


def error(msg: str, **kw: Any) -> None:
    ...


def warn(msg: str, **kw: Any) -> None:
    ...


def info(msg: str, **kw: Any) -> None:
    ...


def init_log() -> None:
    ...


def make_logger(path: str, name: str) -> logging.Logger:
    ...


def make_mem_logger(name: str, to_log: Optional[logging.Handler] = ..., size: int = ...) -> logging.Logger:
    ...


def free_logger(logger: logging.Logger) -> None:
    ...


def pprint(col: str, msg: str, label: str = ..., sep: str = ...) -> None:
    ...
