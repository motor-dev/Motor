from motor_typing import TYPE_CHECKING


class MergeTree(object):
    def __init__(self, state_list):
        # type: (List[LR0DominanceNode]) -> None
        self._node = state_list[0]
        self._children = []
        if len(state_list) > 1:
            self._children.append(MergeTree(state_list[1:]))

    def add_branch(self, state_list):
        # type: (List[LR0DominanceNode]) -> None
        assert state_list[0] == self._node
        if len(state_list) > 1:
            for child in self._children:
                if child._node == state_list[1]:
                    child.add_branch(state_list[1:])
                    return
            else:
                self._children.append(MergeTree(state_list[1:]))


if TYPE_CHECKING:
    from motor_typing import Any, Dict, List, Optional, Tuple
    from .lr0dominancenode import LR0DominanceNode