from typing import Optional, Union
from typing_extensions import Literal


def setdebug() -> None:
    ...


class Hunk(object):
    ...


class PatchSet(object):

    def apply(self, strip: int = ..., root: Optional[str] = ...) -> bool:
        ...


def fromfile(filename: str) -> Union[Literal[False], PatchSet]:
    ...


def fromstring(s: str) -> Union[Literal[False], PatchSet]:
    ...
