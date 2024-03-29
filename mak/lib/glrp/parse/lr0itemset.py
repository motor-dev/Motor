from .lr0item import LR0Item
from .lr0node import LR0Node
from typing import TYPE_CHECKING


class LR0ItemSet(object):

    def __init__(self, index, core):
        # type: (int, List[Tuple[LR0Item, Optional[LR0Node], int]]) -> None
        self._index = index
        self._core = set([])  # type: Set[LR0Node]
        self._items = {}  # type:Dict[LR0Item, LR0Node]
        self._sorted_items = []  # type: List[LR0Item]
        self._discarded = {}  # type: Dict[LR0Item, Set[int]]
        self.add_core(core)
        self._lr0_close()

    def __iter__(self):
        # type: () -> Iterator[LR0Item]
        return iter(self._sorted_items)

    def __getitem__(self, item):
        # type: (LR0Item) -> LR0Node
        return self._items[item]

    def add_core(self, core):
        # type: (List[Tuple[LR0Item, Optional[LR0Node], int]]) -> None
        for item, node, lookahead in core:
            try:
                target_node = self._items[item]
            except KeyError:
                if node is not None:
                    target_node = LR0Node(self, item, predecessor=(lookahead, node))
                else:
                    target_node = LR0Node(self, item)
                self._items[item] = target_node
                self._sorted_items.append(item)
            else:
                assert node is not None
                assert node not in target_node._predecessors
                target_node._predecessors.append(node)
            if node is not None:
                node._successor = target_node
            self._core.add(target_node)

    def _lr0_close(self):
        # type: () -> None
        # Compute the LR(0) closure operation on self._items
        new_items = self._items
        while new_items:
            self._items.update(new_items)
            new_items = {}
            for item in self._sorted_items[::]:
                dn = self._items[item]
                for x in item._after:
                    item = x._item
                    try:
                        successor = self._items[item]
                    except KeyError:
                        try:
                            successor = new_items[item]
                        except KeyError:
                            successor = LR0Node(self, item, parent=dn)
                            new_items[item] = successor
                            self._sorted_items.append(item)
                    if successor not in dn._direct_children:
                        dn._direct_children.append(successor)
                    if dn not in successor._direct_parents:
                        successor._direct_parents.append(dn)
        for node in self._items.values():
            node._direct_parents.sort(key=lambda n: n._item.len - n._item._index)
            node._direct_children.sort(key=lambda n: n._item.len)


if TYPE_CHECKING:
    from typing import Dict, Iterator, List, Optional, Set, FrozenSet, Tuple
