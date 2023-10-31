from typing import BinaryIO, Dict, List, Union

OBJECT = Union[str, int, List["OBJECT"], Dict[str, "OBJECT"]]


def load(fp: BinaryIO) -> OBJECT:
    ...
