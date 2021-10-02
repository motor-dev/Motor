from motor_typing import TYPE_CHECKING


class MergeTree(object):
    def __init__(self, node_set):
        # type: (List[Tuple[LR0Node, str]]) -> None
        self._nodes = {}   # type: Dict[Tuple[int, Tuple[int,...]], MergeNode]
        self._map = {}     # type: Dict[LR0Node, MergeNode]

        for node, tag in node_set:
            self._add_node(node)
        for node, tag in node_set:
            self._map[node].add_tag(tag)

    def _add_node(self, node):
        # type: (LR0Node) -> MergeNode
        try:
            state = self._map[node]
        except KeyError:
            head = node._item.rule.production[:node._item._index]
            key = (node._item._symbol, head)
            try:
                state = self._nodes[key]
                state.add_node(node)
            except KeyError:
                state = MergeNode(len(self._nodes), node._item._symbol, head, node)
                self._nodes[key] = state
            self._map[node] = state
            for parent in node._direct_parents:
                state.add_parent(self._add_node(parent))
            for predecessor in node._predecessors:
                state.add_parent(self._add_node(predecessor))
            return state
        else:
            return state

    def print_dot(self, name_map):
        # type: (List[str]) -> None
        print('digraph MergeTree {')
        for node in self._nodes.values():
            print(
                '  %d[label="[%s]\\n%s ::= %s..."];' %
                (id(node), ', '.join(node._tags), name_map[node._symbol], ' '.join([name_map[s] for s in node._head]))
            )
        for node in self._nodes.values():
            for parent in node._parents:
                print('  %d->%d;' % (id(parent), id(node)))
        print('}')


class MergeNode(object):
    def __init__(self, index, symbol, head, node):
        # type: (int, int, Tuple[int, ...], LR0Node) -> None
        self._index = index
        self._symbol = symbol
        self._head = head
        self._nodes = [node]
        self._parents = []     # type: List[MergeNode]
        self._tags = []        # type: List[str]
        self._merges = node._item._last._merge if node._item._index == 0 else []

    def add_parent(self, parent):
        # type: (MergeNode) -> None
        if parent not in self._parents:
            self._parents.append(parent)

    def add_node(self, node):
        # type: (LR0Node) -> None
        self._nodes.append(node)

    def add_tag(self, tag):
        # type: (str) -> None
        if tag not in self._tags:
            for merge_str, params in self._merges:
                if tag in params:
                    self.add_tag(merge_str)
                    break
            else:
                self._tags.append(tag)
                for parent in self._parents:
                    parent.add_tag(tag)


if TYPE_CHECKING:
    from motor_typing import Dict, List, Tuple
    from .lr0node import LR0Node