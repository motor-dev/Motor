from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .context import State


class Production(object):
    __slots__ = ('_state', '_length')

    def __init__(self, state: "State", prod_len: int) -> None:
        self._state = state
        self._length = prod_len

    def __len__(self):
        # type: () -> int
        return self._length

    def __getitem__(self, index):
        # type: (int) -> Any
        state = self._state
        index += 1
        while index < self._length:
            state = state._parent
            index += 1
        return state._value
