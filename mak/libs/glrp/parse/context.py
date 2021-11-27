from motor_typing import TYPE_CHECKING


class Context(object):
    def __init__(self, parent, param_name):
        # type: (Optional[Context], str) -> None
        self._parent = parent if parent is not None else self
        self._name = param_name
        self._state_stack = [0]    # type: List[int]
        self._sym_stack = []       # type: List[Symbol]

    def split(self, params):
        # type: (List[str]) -> List[Context]
        return [Context(self, param) for param in params]


if TYPE_CHECKING:
    from typing import Optional, List
    from ..symbol import Symbol