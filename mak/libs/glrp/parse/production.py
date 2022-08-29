from ..symbol import Symbol
from motor_typing import TYPE_CHECKING, TypeVar


class Production(Symbol):

    def __init__(self, id, start_position, end_position, production_values, action):
        # type: (int, int, int, List[Symbol], Callable[["Production"], None]) -> None
        Symbol.__init__(self, id, start_position, end_position)
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

    def debug_print(self, name_map, self_indent='', inner_indent=''):
        # type: (List[str], str, str) -> None
        if self._production:
            print('%s%s' % (self_indent, name_map[self._id]))
            for p in self._production[0:-1]:
                p.debug_print(name_map, inner_indent + '\u251c ', inner_indent + '\u2502 ')
            self._production[-1].debug_print(name_map, inner_indent + '\u2570 ', inner_indent + '  ')
        else:
            print('%s%s (nil)' % (self_indent, name_map[self._id]))


class AmbiguousProduction(Symbol):

    def __init__(self, productions):
        # type: (List[Symbol]) -> None
        production = productions[0]
        Symbol.__init__(self, production._id, production._start_position, production._end_position)
        self._productions = productions

    def debug_print(self, name_map, self_indent='', inner_indent=''):
        # type: (List[str], str, str) -> None
        print('%sAmbigous[%s]' % (self_indent, name_map[self._id]))
        for p in self._productions[0:-1]:
            p.debug_print(name_map, inner_indent + '\u255f ', inner_indent + '\u2551 ')
        self._productions[-1].debug_print(name_map, inner_indent + '\u2559 ', inner_indent + '  ')


if TYPE_CHECKING:
    from motor_typing import Any, Callable, List
