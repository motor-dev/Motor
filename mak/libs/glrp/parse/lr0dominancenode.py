from .merge_tree import MergeTree
from motor_typing import TYPE_CHECKING


class LR0DominanceSet(object):
    def __init__(self, node_set, recursive):
        # type: (List[LR0Node], bool) -> None
        self._dominance_nodes = {}     # type: Dict[Tuple[str, Tuple[int,...]], LR0DominanceNode]
        self._map = {}                 # type: Dict[LR0Node, LR0DominanceNode]
        self._roots = []               # type: List[LR0DominanceNode]
        self._dominators = []          # type: List[LR0DominanceNode]
        for node in node_set:
            self._add_node(node, True, recursive)
        self._build_dominance_graph(recursive)
        states = []
        for node in node_set:
            state = self._map[node]
            if state not in states:
                states.append(state)

        self._best_dominator = None    #type: Optional[LR0DominanceNode]
        if recursive:
            self._merge_tree = MergeTree(sorted(states[0]._dominators, key=lambda x: len(x._dominators)))
            for state in states[1:]:
                self._merge_tree.add_branch(sorted(state._dominators, key=lambda x: len(x._dominators)))

            tree = self._merge_tree
            while len(tree._children) == 1:
                tree = tree._children[0]
            self._best_dominator = tree._node
        else:
            common_parents = set(states[0]._dominators)
            for state in states[1:]:
                common_parents.intersection_update(state._dominators)
            if common_parents:
                self._best_dominator = sorted(common_parents, key=lambda x: len(x._dominators))[-1]

    def _add_node(self, node, is_leaf, recursive):
        # type: (LR0Node, bool, bool) -> None
        if node not in self._map:
            head = node._item.rule.production[:node._item._index]
            try:
                state = self._dominance_nodes[(node._item.rule._prod_name, head)]
                state._nodes.append(node)
                state._is_leaf |= is_leaf
            except KeyError:
                state = LR0DominanceNode(len(self._dominance_nodes), head, node, is_leaf)
                if len(head) == 0 and state not in self._roots:
                    self._roots.append(state)
                self._dominance_nodes[(node._item.rule._prod_name, head)] = state
            self._map[node] = state
            for parent in node._direct_parents:
                self._add_node(parent, False, recursive)
            if recursive:
                for predecessor in node._predecessors:
                    self._add_node(predecessor, False, recursive)
        else:
            self._map[node]._is_leaf |= is_leaf

    def _build_dominance_graph(self, recursive):
        # type: (bool) -> None
        all_nodes = set(self._dominance_nodes.values())
        for node, dom_node in self._map.items():
            for parent in node._direct_parents:
                if self._map[parent] not in dom_node._parents:
                    dom_node._parents.append(self._map[parent])
            if recursive:
                for predecessor in node._predecessors:
                    if self._map[predecessor] not in dom_node._parents:
                        dom_node._parents.append(self._map[predecessor])
        for node, dom_node in self._map.items():
            if dom_node._parents:
                dom_node._dominators = all_nodes

        changed = True
        while changed:
            changed = False
            for dom_node in self._dominance_nodes.values():
                if not dom_node._parents:
                    continue
                new_set = set(dom_node._parents[0]._dominators)
                for dom_child in dom_node._parents[1:]:
                    new_set.intersection_update(dom_child._dominators)
                new_set.add(dom_node)
                if new_set != dom_node._dominators:
                    dom_node._dominators = new_set
                    changed = True

        for dom_node in self._dominance_nodes.values():
            for dominator in dom_node._dominators:
                if dominator == dom_node:
                    continue
                elif dom_node._direct_dominator is None:
                    dom_node._direct_dominator = dominator
                elif dom_node._direct_dominator in dominator._dominators:
                    dom_node._direct_dominator = dominator

    def print_dot(self, name_map):
        # type: (List[str]) -> None
        print('digraph Dominance {')
        for (name, head), state in self._dominance_nodes.items():
            print('    %d[label="%s : %s"];' % (id(state), name, ' '.join((name_map[i] for i in head))))
        for state in self._dominance_nodes.values():
            for parent in state._parents:
                print('    %d->%d;' % (id(parent), id(state)))
            #if state._direct_dominator:
            #    print(
            #        '    %d->%d[ltail=cluster_%d,lhead=cluster_%d,color="blue",minlen=3];' % (
            #            id(state._direct_dominator._nodes[0]),
            #            id(state._nodes[0]),
            #            state._direct_dominator._index,
            #            state._index,
            #        )
            #    )
        print('}')

    def print_merge_tree(self, name_map):
        # type: (List[str]) -> None
        def do_print(tree):
            # type: (MergeTree) -> None
            print(
                '    %d[label="%s : %s"];' %
                (id(tree), name_map[tree._node._symbol], ' '.join((name_map[i] for i in tree._node._head)))
            )
            for child in tree._children:
                do_print(child)
                print('    %d->%d;' % (id(tree), id(child)))

        print('digraph Dominance {')
        do_print(self._merge_tree)
        print('}')


class LR0DominanceNode(object):
    def __init__(self, index, head, node, is_leaf):
        # type: (int, Tuple[int, ...], LR0Node, bool) -> None
        self._index = index
        self._head = head
        self._nodes = [node]
        self._parents = []                          # type: List[LR0DominanceNode]
        self._dominators = set([self])
        self._direct_dominator = None               # type: Optional[LR0DominanceNode]
        self._is_leaf = is_leaf
        self._symbol = node._item.rule._prod_symbol #type: int


if TYPE_CHECKING:
    from motor_typing import Any, Dict, List, Optional, Tuple
    from .lr0node import LR0Node