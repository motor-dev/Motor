from motor_typing import TYPE_CHECKING


class Symbol:

    def __init__(self, id, start_position, end_position):
        # type: (int, int, int) -> None
        self._id = id
        self._start_position = start_position
        self._end_position = end_position
        self.value = None  # type: Any

    def debug_print(self, name_map, self_indent='', inner_indent=''):
        # type: (List[str], str, str) -> None
        print('%s"%s"' % (self_indent, name_map[self._id]))


if TYPE_CHECKING:
    from typing import List
    from motor_typing import Any
