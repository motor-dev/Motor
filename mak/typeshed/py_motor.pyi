from typing import Dict, Iterator, List, Optional, Tuple, Union

_MotorValue = Union[
    None,
    int,
    float,
    str,
    Dict["_MotorValue", "_MotorValue"],
    List["_MotorValue"],
    Tuple["_MotorValue", ...]]


class Value(object):
    def __getattr__(self, name: str) -> "Value":
        ...

    def __call__(self, *args: _MotorValue, **kw_args: _MotorValue) -> Optional["Value"]:
        ...

    def __int__(self) -> int:
        ...

    def __str__(self) -> str:
        ...

    def __float__(self) -> float:
        ...

    def __iter__(self) -> Iterator["Value"]:
        ...


class BoundMethod(object):
    def __call__(self, *args: _MotorValue, **kw_args: _MotorValue) -> Optional[Value]:
        ...


class Plugin(object):
    def __init__(self, plugin_name: str) -> None:
        ...

    def __getattr__(self, name: str) -> Value:
        ...


class Log(object):
    ...


stdout: Log = ...
stderr: Log = ...

Motor: Value = ...
