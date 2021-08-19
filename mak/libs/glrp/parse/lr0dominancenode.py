from motor_typing import TYPE_CHECKING


class LR0DominanceSet(object):
    def __init__(self, node_set):
        # type: (List[LR0Node]) -> None
        self._dominance_nodes = {}     # type: Dict[Tuple[str, bool], LR0DominanceNode]
        self._map = {}                 # type: Dict[LR0Node, LR0DominanceNode]
        self._roots = []               # type: List[LR0DominanceNode]
        for node in node_set:
            self._add_node(node, True)
        self._build_dominance_graph()
        states = []
        for node in node_set:
            state = self._map[node]
            if state not in states:
                states.append(state)
        common_dominators = set(states[0]._dominators)
        for state in states[1:]:
            common_dominators.intersection_update(state._dominators)
        self._best_dominator = None    #type: Optional[LR0DominanceNode]
        if common_dominators:
            self._best_dominator = common_dominators.pop()
            for dominator in common_dominators:
                if self._best_dominator in dominator._dominators:
                    self._best_dominator = dominator

    def _add_node(self, node, is_leaf):
        # type: (LR0Node, bool) -> None
        if node not in self._map:
            is_root = node._item._index == 0
            try:
                state = self._dominance_nodes[(node._item.rule._prod_name, is_root)]
                state._nodes.append(node)
                state._is_leaf |= is_leaf
            except KeyError:
                state = LR0DominanceNode(len(self._dominance_nodes), node, is_leaf)
                if is_root and state not in self._roots:
                    self._roots.append(state)
                self._dominance_nodes[(node._item.rule._prod_name, is_root)] = state
            self._map[node] = state
            for parent in node._direct_parents:
                self._add_node(parent, False)
        else:
            self._map[node]._is_leaf |= is_leaf

    def _build_dominance_graph(self):
        # type: () -> None
        all_nodes = set(self._dominance_nodes.values())
        for node, dom_node in self._map.items():
            for parent in node._direct_parents:
                if self._map[parent] not in dom_node._parents:
                    dom_node._parents.append(self._map[parent])
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

    def print_dot(self):
        # type: () -> None
        print('digraph Dominance {')
        print('    compound = True;')
        for (name, is_root), state in self._dominance_nodes.items():
            print('    subgraph cluster_%d {' % state._index)
            print('        label = "%s";' % name)
            if state == self._best_dominator:
                print('        style="filled";')
                print('        color="green";')
            elif state._is_leaf:
                print('        style="filled";')
                print('        color="lightgrey";')
            elif is_root:
                print('        style="filled";')
                print('        color="lightblue";')
            for node in state._nodes:
                print('        %d[label="%s"];' % (id(node), node._item.rule._debug_str))
            print('    }')
        for node in self._map:
            for node_parent in node._direct_parents:
                print('    %d->%d[style=dotted];' % (id(node_parent), id(node)))
        for state in self._dominance_nodes.values():
            for parent in state._parents:
                #if parent != state._direct_dominator:
                print(
                    '    %d->%d[ltail=cluster_%d,lhead=cluster_%d,minlen=3];' %
                    (id(parent._nodes[0]), id(state._nodes[0]), parent._index, state._index)
                )
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


class LR0DominanceNode(object):
    def __init__(self, index, node, is_leaf):
        # type: (int, LR0Node, bool) -> None
        self._index = index
        self._nodes = [node]
        self._parents = []             # type: List[LR0DominanceNode]
        self._dominators = set([self])
        self._direct_dominator = None  # type: Optional[LR0DominanceNode]
        self._is_leaf = is_leaf


if TYPE_CHECKING:
    from motor_typing import Dict, List, Optional, Tuple
    from .lr0node import LR0Node