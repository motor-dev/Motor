from ..symbol import Symbol
from ..position import Position
from motor_typing import TYPE_CHECKING, TypeVar


class Production(Symbol):
    def __init__(self, id, name, position, production_values, action):
        # type: (int, str, Position, List[Symbol], Callable[[Production], None]) -> None
        Symbol.__init__(self, id, name, position)
        self._production = production_values
        self._action = action

    def _insert(self, index, value):
        # type: (int, Symbol) -> None
        assert index > 0
        self._production.insert(index, value)

    def run(self):
        # type: () -> None
        self._action(self)

    def __getitem__(self, index):
        # type: (int) -> Any
        if index == 0:
            return self.value
        elif index > 0:
            return self._production[index - 1].value

    def __setitem__(self, index, value):
        # type: (int, Any) -> None
        if index == 0:
            self.value = value
        else:
            raise IndexError('can only assign to production[0]')


if TYPE_CHECKING:
    from motor_typing import Any, Callable, List
