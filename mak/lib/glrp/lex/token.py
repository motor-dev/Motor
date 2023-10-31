from ..symbol import Symbol
from typing import Any, List, Tuple


class Token(Symbol):

    def __init__(
            self, id: int, lexer: "Lexer", position: Tuple[int, int], value: Any, skipped_tokens: List["Token"]
    ) -> None:
        Symbol.__init__(self, id, position)
        self.value = value
        self._skipped_tokens = skipped_tokens
        self._lexer = lexer

    def duplicate(self) -> "Token":
        return Token(self._id, self._lexer, self.position, self.value, [])

    def text(self) -> str:
        return self._lexer.text(self)

    def debug_print(self, name_map: List[str], self_indent: str = '', inner_indent: str = '') -> None:
        text = self.text()
        if text != name_map[self._id]:
            print('%s%s "%s"' % (self_indent, name_map[self._id], text))
        else:
            print('%s%s' % (self_indent, name_map[self._id]))

    @property
    def skipped_tokens(self) -> List["Token"]:
        return self._skipped_tokens


from .lexer import Lexer
