from typing import Optional, List
from .Task import Task


class WafError(Exception):
    def __init__(self, msg: str = '', ex: Optional[Exception] = None) -> None:
        ...

    def __str__(self) -> str:
        ...


class BuildError(WafError):
    def __init__(self, error_tasks: List[Task] = ...):
        ...

    def format_error(self) -> str:
        ...


class ConfigurationError(WafError):
    ...


class TaskRescan(WafError):
    ...


class TaskNotReady(WafError):
    ...
