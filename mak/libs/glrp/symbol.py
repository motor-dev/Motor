from typing import Any, List, Tuple


class Symbol:

    def __init__(self, id: int, position: Tuple[int, int]) -> None:
        self._id = id
        self.position = position
        self.value = None  # type: Any

    def debug_print(self, name_map: List[str], self_indent: str = '', inner_indent: str = '') -> None:
        print('%s"%s"' % (self_indent, name_map[self._id]))

    @property
    def id(self):
        return self._id
