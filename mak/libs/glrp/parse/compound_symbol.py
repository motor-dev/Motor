from ..symbol import Symbol
from motor_typing import TYPE_CHECKING


class CompoundSymbol(Symbol):

    def __init__(self, id, start_position, end_position, production_values):
        # type: (int, int, int, List[Symbol]) -> None
        Symbol.__init__(self, id, start_position, end_position)
        self._production = production_values

    def debug_print(self, name_map, self_indent='', inner_indent=''):
        # type: (List[str], str, str) -> None
        if self._production:
            print('%s%s' % (self_indent, name_map[self._id]))
            for p in self._production[0:-1]:
                p.debug_print(name_map, inner_indent + '\u251c ', inner_indent + '\u2502 ')
            self._production[-1].debug_print(name_map, inner_indent + '\u2570 ', inner_indent + '  ')
        else:
            print('%s%s (nil)' % (self_indent, name_map[self._id]))


class AmbiguousSymbol(Symbol):

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
    from motor_typing import List
