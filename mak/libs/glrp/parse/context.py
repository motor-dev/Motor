from motor_typing import TYPE_CHECKING


class Context(object):

    def __init__(self, parent, param_name):
        # type: (Optional[Context], str) -> None
        if parent is None:
            self._parent = self
            self._name = param_name
            self._state_stack = [0]    # type: List[int]
            self._sym_stack = []       # type: List[Symbol]
        else:
            self._parent = parent
            self._name = param_name
            self._state_stack = parent._state_stack[:]
            self._sym_stack = parent._sym_stack[:]


if TYPE_CHECKING:
    from typing import List, Optional
    from ..symbol import Symbol