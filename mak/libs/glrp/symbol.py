from motor_typing import TYPE_CHECKING


class Symbol:
    def __init__(self, id, start_position, end_position):
        # type: (int, int, int) -> None
        self._id = id
        self._start_position = start_position
        self._end_position = end_position
        self.value = None  # type: Any


if TYPE_CHECKING:
    from motor_typing import Any
