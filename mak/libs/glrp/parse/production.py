from ..symbol import Symbol
from motor_typing import TYPE_CHECKING


class Production(object):

    def __init__(self, context, prod_len):
        # type: (Context, int) -> None
        self._context = context
        self._index = len(self._context._prod_stack) - prod_len

    def __len__(self):
        # type: () -> int
        return len(self._context._prod_stack) - self._index

    def __getitem__(self, index):
        # type: (int) -> Any
        context = self._context
        index += self._index
        assert index >= 0
        return context._prod_stack[index]


if TYPE_CHECKING:
    from typing import Any
    from .context import Context
