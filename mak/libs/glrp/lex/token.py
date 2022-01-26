from ..symbol import Symbol
from motor_typing import TYPE_CHECKING


class Token(Symbol):
    def __init__(self, id, start_position, end_position, value, skipped_tokens):
        # type: (int, int, int, Any, List[Token]) -> None
        Symbol.__init__(self, id, start_position, end_position)
        self.value = value
        self._skipped_tokens = skipped_tokens


if TYPE_CHECKING:
    from motor_typing import Any, List
