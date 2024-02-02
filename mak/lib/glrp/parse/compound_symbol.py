from ..symbol import Symbol
from typing import List, Tuple


class CompoundSymbol(Symbol):
    __slots__ = ('_production')

    def __init__(self, id: int, position: Tuple[int, int], production_values: List[Symbol]) -> None:
        Symbol.__init__(self, id, position)
        self._production = production_values

    def debug_print(self, name_map: List[str], self_indent: str = '', inner_indent: str = '') -> None:
        if self._production:
            print('%s%s' % (self_indent, name_map[self._id]))
            for p in self._production[0:-1]:
                p.debug_print(name_map, inner_indent + '\u251c ', inner_indent + '\u2502 ')
            self._production[-1].debug_print(name_map, inner_indent + '\u2570 ', inner_indent + '  ')
        else:
            print('%s%s (nil)' % (self_indent, name_map[self._id]))


class AmbiguousSymbol(Symbol):
    __slots__ = ('_productions')

    def __init__(self, productions: List[Symbol]) -> None:
        production = productions[0]
        Symbol.__init__(self, production._id, production.position)
        self._productions = productions

    def debug_print(self, name_map: List[str], self_indent: str = '', inner_indent: str = '') -> None:
        print('%sAmbigous[%s]' % (self_indent, name_map[self._id]))
        for p in self._productions[0:-1]:
            p.debug_print(name_map, inner_indent + '\u255f ', inner_indent + '\u2551 ')
        self._productions[-1].debug_print(name_map, inner_indent + '\u2559 ', inner_indent + '  ')
