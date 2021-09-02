from motor_typing import TYPE_CHECKING
import functools
from .lr0path import LR0PathItem


class LR0Node(object):
    def __init__(self, item_set, item, predecessor=None, parent=None):
        # type: (LR0ItemSet, LR0Item, Optional[Tuple[int, "LR0Node"]], Optional[LR0Node]) -> None
        self._item_set = item_set
        self._item = item
        self._parents = set()                            # type: Set[LR0Node]
        self._parents_core = set()                       # type: Set[LR0Node]
        self._path_cache = {
        }                                                # type: Dict[Optional[int], Tuple[LR0Path, Set[Union[Tuple[LR0Node, Optional[int]], LR0ItemSet]], List[Tuple[LR0Node, LR0Path, Optional[int], Optional[int]]]]]
        if predecessor is not None:
            self._predecessor_lookahead = predecessor[0] # type: Optional[int]
            self._predecessors = [predecessor[1]]
        else:
            self._predecessor_lookahead = None
            self._predecessors = []
        self._successor = None                           # type: Optional[LR0Node]

        self._direct_parents = []
        self._direct_children = []     # type: List[LR0Node]
        if parent is not None:
            self._direct_parents.append(parent)
            parent._direct_children.append(self)

    def expand_empty(self):
        # type: () -> LR0Path
        # expand the first item of the path to build empty productions
        if self._item._index == self._item.len:
            return LR0PathItem(self._item)
        for child in self._direct_children:
            if -1 not in child._item._first:
                continue
            if child._successor is None:
                result = LR0PathItem(child._item) # type: LR0Path
                result = result.derive_from(self._item)
                return result
            else:
                if -1 in child._item._follow:
                    p = child._successor.expand_empty()
                    result = child.expand_empty()
                    result = result.expand_next(p)
                    result = result.derive_from(self._item)
                    return result
        raise ValueError()

    def expand_lookahead(self, lookahead):
        # type: (int) -> LR0Path
        # expand the first item of the path until it starts with the lookahead
        queue = [(self, [[]])]     # type: List[Tuple[LR0Node, List[List[LR0Path]]]]
        seen = set()

        while queue:
            node, paths = queue.pop(0)
            if node in seen:
                continue
            seen.add(node)

            if node._item != node._item._last:
                following_symbol = node._item.rule.production[node._item._index]
                if following_symbol == lookahead:
                    previous = None
                    paths[-1].append(LR0PathItem(node._item))
                    while paths:
                        child_paths = paths.pop(-1)
                        if previous is not None:
                            child_paths[-1] = child_paths[-1].expand_next(previous)
                        merge_children = lambda x, y: x.derive_from(y._items[0][1])
                        result = functools.reduce(merge_children, child_paths[::-1])
                        previous = result
                    return result
                elif lookahead in node._item._first:
                    for child in node._direct_children:
                        queue.append((child, paths[:-1] + [paths[-1] + [LR0PathItem(node._item)]]))
                elif -1 in node._item._first and node._successor is not None:
                    empty_path = node.expand_empty()
                    queue.append((node._successor, paths[:-1] + [paths[-1] + [empty_path]] + [[]]))
        raise ValueError()

    def filter_node_by_lookahead(self, path, lookahead):
        # type: (LR0Path, Optional[int]) -> LR0Path
        following_symbol = self._item.rule.production[self._item._index + 1]
        assert self._successor is not None
        if lookahead == following_symbol:
            return path
        elif lookahead in self._successor._item._first:
            successor_path = self._successor.expand_lookahead(lookahead)
            return path.expand_next(successor_path)
        elif -1 in self._successor._item._first:
            successor_path = self._successor.expand_empty()
            p = self._successor.filter_node_by_lookahead(successor_path, lookahead)
            return path.expand_next(p)
        else:
            raise ValueError()

    def backtrack_up(self, path, lookahead, seen):
        # type: (LR0Path, Optional[int], Set[Union[Tuple["LR0Node", Optional[int]], LR0ItemSet]]) -> List[Tuple["LR0Node", LR0Path, Optional[int], Optional[int]]]
        if self._item_set not in seen:
            try:
                original_path, original_visited, result = self._path_cache[lookahead]
            except KeyError:
                pass
            else:
                seen.update(original_visited)
                return [(node, p.patch(original_path, path), la, consumed) for node, p, la, consumed in result]

        queue = [(self, path, lookahead)]
        result = []
        state_seen = set()     # type: Set[Union[Tuple["LR0Node", Optional[int]], LR0ItemSet]]
        state_path_seen = set()

        seen.add(self._item_set)
        state_seen.add(self._item_set)

        #self._path_cache[lookahead] = (path, state_seen, result)

        while queue:
            node, path, lookahead = queue.pop(0)

            for parent in node._direct_parents:
                if (parent, lookahead) in seen:
                    continue
                seen.add((parent, lookahead))
                state_seen.add((parent, lookahead))
                item = parent._item
                if lookahead is not None:
                    if lookahead in item._follow:
                        p = parent.filter_node_by_lookahead(path.derive_from(parent._item), lookahead)
                        result.append((parent, p, None, None))
                        queue.append((parent, p, None))
                    if -1 in item._follow:
                        queue.append((parent, path.derive_from(parent._item), lookahead))
                else:
                    queue.append((parent, path.derive_from(parent._item), lookahead))
            for predecessor in node._predecessors:
                if lookahead is None:
                    if (predecessor._item_set, predecessor._item._symbol) in state_path_seen:
                        continue
                    state_path_seen.add((predecessor._item_set, predecessor._item._symbol))
                assert node._predecessor_lookahead is not None
                result.append((predecessor, path.extend(predecessor._item), lookahead, node._predecessor_lookahead))

        return result

    def backtrack_to_any(self, path, nodes):
        # type: (LR0Path, List["LR0Node"]) -> Tuple["LR0Node", LR0Path]
        if self in nodes:
            return self, path
        queue = [(self, path)]
        seen = set()
        seen.add(self)
        while queue:
            node, path = queue.pop(0)

            for parent in node._direct_parents:
                if parent in seen:
                    continue
                seen.add(parent)
                if parent in nodes:
                    return parent, path.derive_from(parent._item)
                else:
                    queue.append((parent, path.derive_from(parent._item)))

        raise ValueError()


if TYPE_CHECKING:
    from motor_typing import List, Optional, Set, Optional, Tuple, Dict, Union
    from .lr0item import LR0Item
    from .lr0path import LR0Path
    from .lr0itemset import LR0ItemSet