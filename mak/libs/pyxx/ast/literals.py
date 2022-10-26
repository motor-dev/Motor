from motor_typing import TYPE_CHECKING


class Literal(object):
    pass


class BracedInitList(Literal):

    def __init__(self):
        # type: () -> None
        pass


class StringLiteral(Literal):

    def __init__(self, string):
        # type: (str) -> None
        self._string = string


if TYPE_CHECKING:
    from typing import Any, List, Tuple
