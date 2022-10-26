from ..symbol import Symbol
from motor_typing import TYPE_CHECKING


class Token(Symbol):

    def __init__(self, id, lexer, start_position, end_position, value, skipped_tokens):
        # type: (int, Lexer, int, int, Any, List[Token]) -> None
        Symbol.__init__(self, id, start_position, end_position)
        self.value = value
        self._skipped_tokens = skipped_tokens
        self._lexer = lexer

    def duplicate(self):
        # type: () -> Token
        return Token(self._id, self._lexer, self._start_position, self._end_position, self.value, [])

    def text(self):
        # type: () -> str
        return self._lexer.text(self)

    def debug_print(self, name_map, self_indent='', inner_indent=''):
        # type: (List[str], str, str) -> None
        text = self.text()
        if text != name_map[self._id]:
            print('%s%s "%s"' % (self_indent, name_map[self._id], text))
        else:
            print('%s%s' % (self_indent, name_map[self._id]))


if TYPE_CHECKING:
    from motor_typing import Any, List
    from .lexer import Lexer
