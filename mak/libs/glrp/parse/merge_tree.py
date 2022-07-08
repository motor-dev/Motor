from motor_typing import TYPE_CHECKING


class MergeTree(object):

    _cache = {}    # type: Dict[Tuple[Tuple[LR0Node, bool, FrozenSet[int]], ...], MergeState]

    def __init__(self, node_set, lookaheads):
        # type: (List[Tuple[LR0Node, bool, str]], Set[int]) -> None
        self._map = {}                 # type: Dict[Tuple[LR0Node, int], MergeNode]
        self._error_nodes = {}         # type: Dict[LR0Item, Set[str]]
        self._leaves = []              # type: List[MergeState]
        self._leaf_nodes = []          # type: List[MergeNode]
        self._important_states = set() # type: Set[MergeState]

        root_state, all_states, important_states = self._add_nodes(node_set, lookaheads)
        print(len(all_states), len(important_states))
        merge_states = {}  # type: Dict[Tuple[LR0Item, int], List[MergeState]]
        for state in important_states:
            self._set_tags(state, merge_states)
                           #important_states = self._set_tags(node_set, root_state, all_states)

        #for state_list in important_states.values():
        #    path_list = [
        #        self._get_important_states(state, self._important_states, root_state, all_states)
        #        for state in state_list
        #    ]
        #    self._important_states.update(sorted(path_list, key=lambda x: len(x))[0])
        #self._important_states.update(all_states)

    def check_resolved(self, name_map, logger):
        # type: (List[str], Logger) -> None
        #merge_node = self._map[root_node._item]
        #if len(merge_node._tags) > 1:
        #    logger.warning('   merge conflicts: [%s]' % ', '.join(merge_node._tags))
        self.print_dot(name_map, logger)
        pass

    def _set_tags(self, state, important_states):
        # type: (MergeState, Dict[Tuple[LR0Item, int], List[MergeState]]) -> None
        merges = {}    # type: Dict[Tuple[MergeNode, int], Tuple[Set[int], str]]

        for node, _, indices in state._entry:
            merge_node = self._map[(node, state._index)]
            merges[(merge_node, -1)] = set(indices)
            for i in indices:
                merge_node._tags[tag] = set([i])
        merge_list = list(merges)
        while merge_list:
            (merge_node, merge_index) = merge_list.pop(0)
            indices, tag = merges.pop((merge_node, merge_index))
            if merge_index != -1:
                if len(indices) == len(merge_node._indices):
                    assert indices == merge_node._indices
                    resolve_type = 0
                else:
                    resolve_type = 1
                try:
                    important_states[(merge_node._item, resolve_type)].append(merge_node._state)
                except KeyError:
                    important_states[(merge_node._item, resolve_type)] = [merge_node._state]
                if resolve_type == 0:
                    continue
            queue = [(merge_node, indices, tag)]
            while queue:
                merge_node, indices, tag = queue.pop(0)
                for index, (merge_result, merged_tags) in enumerate(merge_node._merges):
                    if tag in merged_tags:
                        for parent_node in merge_node._parents:
                            try:
                                parent_node._tags[merge_result].update(indices)
                            except KeyError:
                                parent_node._tags[merge_result] = set(indices)
                            parent_node._indices.update(indices)
                            try:
                                merge_indices, merge_tag = merges[(parent_node, index)]
                            except KeyError:
                                merge_list.append((parent_node, index))
                                merges[(parent_node, index)] = (set(indices), merge_result)
                            else:
                                merge_indices.update(indices)
                                assert merge_tag == merge_result
                            merge_node._merge_result = merge_result
                        break
                else:
                    for parent_node in merge_node._parents:
                        if tag in parent_node._tags and indices.issubset(parent_node._indices):
                            continue
                        try:
                            parent_node._tags[tag].update(indices)
                        except KeyError:
                            parent_node._tags[tag] = set(indices)
                        parent_node._indices.update(indices)
                        queue.append((parent_node, indices, tag))

        return important_states

    def backtrack_up(self, node, lookaheads):
        # type: (LR0Node, Set[int]) -> List[Tuple[LR0Node, bool, int]]
        queue = [(node, lookaheads)]
        result = []    # type: List[Tuple[LR0Node, bool, int]]
        seen = set()

        while queue:
            node, lookaheads = queue.pop(0)

            for parent in node._direct_parents:
                if (parent, len(lookaheads) > 0) in seen:
                    continue
                seen.add((parent, len(lookaheads) > 0))
                item = parent._item
                if lookaheads:
                    if not lookaheads.isdisjoint(item._follow):
                        queue.append((parent, set()))
                    if -1 in item._follow:
                        queue.append((parent, lookaheads))
                else:
                    queue.append((parent, lookaheads))
            for predecessor in node._predecessors:
                assert node._predecessor_lookahead is not None
                result.append((predecessor, len(lookaheads) > 0, node._predecessor_lookahead))

        return result

    def _add_nodes(self, node_set, lookaheads):
        # type: (List[Tuple[LR0Node, bool, str]], Set[int]) -> Tuple[MergeState, Set[MergeState], Set[MergeState]]
        index = 1
        root = MergeState(
            tuple((node, lookahead, frozenset([i])) for i, (node, lookahead, _) in enumerate(node_set)),
            node_set[0][0]._item_set, index
        )
        important_states = set()
        reduce_indices = set()
        for i, (_, lookahead, _) in enumerate(node_set):
            if lookahead:
                reduce_indices.add(i)

        states = {}    # type: Dict[Tuple[Tuple[LR0Node, bool, FrozenSet[int]], ...], MergeState]
        states[root._entry] = root
        state_set = set(states.values())

        queue = [(root, node_set[0][0]._item_set)]

        while queue:
            state, item_set = queue.pop(0)
            index += 1
            new_states = {}    # type: Dict[Tuple[LR0ItemSet, int], Dict[Tuple[LR0Node, bool], Set[int]]]

            if item_set._index == 0:
                self._leaves.append(state)

            has_merge = False
            seen = {}  # type: Dict[LR0Node, LR0Node]
            for node, search_lookahead, indices in state._entry:
                predecessor_list = self.backtrack_up(node, lookaheads if search_lookahead else set())
                for predecessor, search_lookahead, consumed_symbol in predecessor_list:
                    try:
                        has_merge |= seen[predecessor] != node
                    except KeyError:
                        seen[predecessor] = node
                    try:
                        predecessors = new_states[(predecessor._item_set, consumed_symbol)]
                    except KeyError:
                        predecessors = {}
                        new_states[(predecessor._item_set, consumed_symbol)] = predecessors
                    try:
                        predecessors[(predecessor, search_lookahead)].update(indices)
                    except KeyError:
                        predecessors[(predecessor, search_lookahead)] = set(indices)

            if has_merge:
                state._has_merge = has_merge
                important_states.add(state)

            for (item_set, consumed_lookahead
                 ), predecessors in sorted(new_states.items(), key=lambda x: (x[0][0]._index, x[0][1])):
                entry = tuple(
                    sorted(
                        ((node, lookahead, frozenset(indices)) for (node, lookahead), indices in predecessors.items()),
                        key=lambda x: (x[0]._item.rule._filename, x[0]._item.rule._lineno, x[0]._item._index, x[1])
                    )
                )

                all_indices = set()    # type: Set[int]
                for (node, lookahead, indices) in entry:
                    all_indices.update(indices)

                if len(all_indices) >= 2 and len(all_indices.intersection(reduce_indices)) >= 1:
                    try:
                        new_state = states[entry]
                    except KeyError:
                        search_lookahead = False
                        for (_, lookahead) in predecessors:
                            search_lookahead |= lookahead
                        new_state = MergeState(entry, item_set, index)
                        state_set.add(new_state)
                        states[entry] = new_state
                        queue.append((new_state, item_set))
                    new_state._prev.add(state)
                    state._next.add(new_state)

        for leaf in self._leaves:
            for node, lookahead, indices in leaf._entry:
                for i in indices:
                    leaf._finalize(i)

        self._build_tree(important_states, lookaheads)
        return root, state_set, important_states

    def _build_tree(self, states, lookaheads):
        # type: (Set[MergeState], Set[int]) -> None
        for state in states:
            merge_nodes_indices = {}   # type: Dict[MergeNode, Set[int]]
            item_set = state._item_set
            heads = []
            for node, lookahead, indices in state._entry:
                if not indices.isdisjoint(state._target):
                    heads.append((node, state, lookahead))
            if not heads:
                continue
            targets = {}
            if state._next:
                for next in state._next:
                    if next not in states:
                        continue
                    for node, lookahead, indices in next._entry:
                        if not indices.isdisjoint(state._target):
                            targets[(node, lookahead)] = next
                            if (node, next._index) not in self._map:
                                merge_node = MergeNode(node._item, next)
                                try:
                                    merge_nodes_indices[merge_node].update(indices)
                                except KeyError:
                                    merge_nodes_indices[merge_node] = set(indices)
                                self._map[(node, next._index)] = merge_node
            else:
                assert item_set._index == 0
                assert len(item_set._core) == 1
                n = list(item_set._core)[0]
                targets[(n, False)] = state
                if (n, state._index) not in self._map:
                    leaf_node = MergeNode(n._item, state)
                    target_indices = [i for i, t in enumerate(state._target) if t]
                    try:
                        merge_nodes_indices[leaf_node].update(target_indices)
                    except KeyError:
                        merge_nodes_indices[leaf_node] = set(target_indices)
                    self._leaf_nodes.append(leaf_node)
                    self._map[(n, state._index)] = leaf_node

            for node, state, _ in heads:
                if (node, state._index) not in self._map:
                    self._map[(node, state._index)] = MergeNode(node._item, state)
            state = heads[0][1]

            queue = list(targets)
            seen = set()
            while queue:
                node, la = queue.pop(0)
                if (node, la) in seen:
                    continue
                seen.add((node, la))
                if node._item_set != item_set:
                    assert node._successor is not None
                    if (node._successor, la) not in targets:
                        targets[(node._successor, la)] = state
                    queue.append((node._successor, la))
                else:
                    item = node._item
                    if la:
                        if -1 in item._follow:
                            for child in node._direct_children:
                                if (child, True) not in targets:
                                    targets[(child, True)] = state
                                queue.append((child, True))
                    else:
                        if not lookaheads.isdisjoint(item._follow):
                            for child in node._direct_children:
                                if (child, True) not in targets:
                                    targets[(child, True)] = state
                                queue.append((child, True))
                        for child in node._direct_children:
                            if (child, False) not in targets:
                                targets[(child, False)] = state
                            queue.append((child, False))

            seen2 = set()
            queue2 = []
            for head, state, la in heads:
                merge_node = self._map[(head, state._index)]
                queue2.append((head, la, merge_node))

            while queue2:
                node, la, merge_node = queue2.pop(0)
                if (node, la) not in targets:
                    continue
                if (node, la, merge_node) in seen2:
                    continue
                seen2.add((node, la, merge_node))

                for parent_node in node._direct_parents:
                    item = parent_node._item
                    if la:
                        try:
                            state = targets[(parent_node, False)]
                        except KeyError:
                            pass
                        else:
                            if not lookaheads.isdisjoint(item._follow):
                                try:
                                    parent_merge_node = self._map[(parent_node, state._index)]
                                except KeyError:
                                    parent_merge_node = MergeNode(item, state)
                                    self._map[(parent_node, state._index)] = parent_merge_node
                                merge_node._parents.add(parent_merge_node)
                                parent_merge_node._children.add(merge_node)
                                queue2.append((parent_node, False, parent_merge_node))
                        try:
                            state = targets[(parent_node, True)]
                        except KeyError:
                            pass
                        else:
                            if -1 in item._follow:
                                try:
                                    parent_merge_node = self._map[(parent_node, state._index)]
                                except KeyError:
                                    parent_merge_node = MergeNode(item, state)
                                    self._map[(parent_node, state._index)] = parent_merge_node
                                merge_node._parents.add(parent_merge_node)
                                parent_merge_node._children.add(merge_node)
                                queue2.append((parent_node, True, parent_merge_node))
                    else:
                        try:
                            state = targets[(parent_node, la)]
                        except KeyError:
                            pass
                        else:
                            try:
                                parent_merge_node = self._map[(parent_node, state._index)]
                            except KeyError:
                                parent_merge_node = MergeNode(item, state)
                                self._map[(parent_node, state._index)] = parent_merge_node
                            merge_node._parents.add(parent_merge_node)
                            parent_merge_node._children.add(merge_node)
                            queue2.append((parent_node, la, parent_merge_node))
                for predecessor in node._predecessors:
                    try:
                        state = targets[(predecessor, la)]
                    except KeyError:
                        pass
                    else:
                        try:
                            parent_merge_node = self._map[(predecessor, state._index)]
                        except KeyError:
                            parent_merge_node = MergeNode(predecessor._item, state)
                            self._map[(predecessor, state._index)] = parent_merge_node
                        merge_node._parents.add(parent_merge_node)
                        parent_merge_node._children.add(merge_node)

            queue3 = []
            for merge_node, frozen_indices in merge_nodes_indices.items():
                queue3.append((merge_node, frozen_indices))

            while queue3:
                merge_node, frozen_indices = queue3.pop()
                if frozen_indices.issubset(merge_node._indices):
                    continue
                merge_node._indices.update(frozen_indices)
                for child_node in merge_node._children:
                    queue3.append((child_node, merge_node._indices))

    def _get_important_states(self, state, important_states, root_state, all_states):
        # type: (MergeState, Set[MergeState], MergeState, Set[MergeState]) -> List[MergeState]
        origin = state
        queue = [(origin, [origin])]
        seen = set()
        while queue:
            state, path = queue.pop(0)
            if state in important_states:
                break
            if state in self._leaves:
                path.append(state)
                break
            if state in seen:
                continue
            seen.add(state)
            for state in state._next:
                queue.append((state, path + [state]))
        else:
            assert False

        seen = set()
        queue = [(origin, path)]
        while queue:
            state, path = queue.pop(0)
            if state == root_state:
                return path
            if state in seen:
                continue
            seen.add(state)
            for state in state._prev:
                if state in all_states:
                    if state not in important_states:
                        queue.append((state, path + [state]))
                    else:
                        queue.insert(0, (state, path))

        assert False

    def print_dot(self, name_map, out_stream):
        # type: (List[str], Logger) -> None
        out_stream.info('   digraph MergeTree {')
        out_stream.info('     node[style="rounded,filled"][shape="box"];')
        colors = [
            'aliceblue', 'aquamarine', 'burlywood', 'cadetblue1', 'coral', 'darkgoldenrod1', 'darkolivegreen1',
            'darkslategray2', 'deepskyblue', 'gray', 'khaki1', 'lightpink1', 'mistyrose', 'palegreen1', 'rosybrown2',
            'thistle', 'wheat1'
        ]
        tags = {}  # type: Dict[str, str]

        def get_color(tag):
            # type: (str) -> str
            try:
                return tags[tag]
            except KeyError:
                result = colors[len(tags)]
                tags[tag] = result
                return result

        states = {}    # type: Dict[Tuple[int, int], List[MergeNode]]

        for (node, index), merge_node in self._map.items():
            if merge_node._state in self._important_states:
                try:
                    states[(index, node._item_set._index)].append(merge_node)
                except KeyError:
                    states[(index, node._item_set._index)] = [merge_node]

        for (index, state_number), node_list in states.items():
            out_stream.info('     subgraph cluster_%d {' % (index))
            out_stream.info('       label="State %d"; style="rounded";' % (state_number))

            node_index = {}                                                                                  # type: Dict[str, List[MergeNode]]
            for merge_node in node_list:
                if merge_node._merge_result:
                    try:
                        node_index[merge_node._merge_result].append(merge_node)
                    except KeyError:
                        node_index[merge_node._merge_result] = [merge_node]
                else:
                    color = ':'.join([get_color(tag) for tag in merge_node._tags])
                    if merge_node._split and len(merge_node._tags) > 1:
                        border_color = '[color=red][penwidth=3]'
                        try:
                            self._error_nodes[merge_node._item].update(merge_node._tags)
                        except KeyError:
                            self._error_nodes[merge_node._item] = set(merge_node._tags)
                    else:
                        border_color = ''
                    out_stream.info(
                        '       %d[label="%s[%s]\\n%s"]%s[fillcolor="%s"];' % (
                            id(merge_node), name_map[merge_node._item._symbol], ', '.join(merge_node._tags),
                            merge_node._item.to_short_string(name_map), border_color, color
                        )
                    )

            for merge_result, merge_nodes in node_index.items():
                merged_tags = set()    # type: Set[str]
                for merge_node in merge_nodes:
                    merged_tags.update(merge_node._tags)

                out_stream.info('       subgraph cluster_%s_%d {' % (merge_result, index))
                out_stream.info(
                    '         label="%s => %s"; style="rounded,filled"; color="pink";' %
                    ('/'.join(merged_tags), merge_result)
                )

                for merge_node in merge_nodes:
                    if merge_node._split and len(merge_node._tags) > 1:
                        border_color = '[color=red][penwidth=3]'
                        try:
                            self._error_nodes[merge_node._item].update(merge_node._tags)
                        except KeyError:
                            self._error_nodes[merge_node._item] = set(merge_node._tags)
                    else:
                        border_color = ''
                    color = ':'.join([get_color(tag) for tag in merge_node._tags])
                    border_color = ''
                    out_stream.info(
                        '           %d[label="%s[%s]\\n%s"]%s[fillcolor="%s"];' % (
                            id(merge_node), name_map[merge_node._item._symbol], ', '.join(merge_node._tags),
                            merge_node._item.to_short_string(name_map), border_color, color
                        )
                    )
                out_stream.info('       }')
            out_stream.info('     }')

        for _, merge_node in self._map.items():
            if merge_node._state in self._important_states:
                for parent in merge_node._parents:
                    if parent._state in self._important_states:
                        out_stream.info('     %d->%d;' % (id(parent), id(merge_node)))
        out_stream.info('   }')


class MergeState(object):

    def __init__(self, entry, item_set, index):
        # type: (Tuple[Tuple[LR0Node, bool, FrozenSet[int]], ...], LR0ItemSet, int) -> None
        self._entry = entry
        self._index = index
        self._target = set()            # type: Set[int]
        self._prev = set()              # type: Set[MergeState]
        self._next = set()              # type: Set[MergeState]
        self._item_set = item_set
        self._important_parents = set() # type: Set[MergeState]
        self._has_merge = False

    def _finalize(self, index):
        # type: (int) -> None
        if index not in self._target:
            self._target.add(index)
            for prev in self._prev:
                prev._finalize(index)


class MergeNode(object):

    def __init__(self, item, state):
        # type: (LR0Item, MergeState) -> None
        self._item = item
        self._merges = self._item._index == 0 and self._item._last._merge or []
        self._state = state
        self._tags = {}            # type: Dict[str, Set[int]]
        self._parents = set()      # type: Set[MergeNode]
        self._children = set()     # type: Set[MergeNode]
        self._merge_result = ''
        self._split = bool(self._item._split)
        self._indices = set()      # type: Set[int]


if TYPE_CHECKING:
    from motor_typing import Dict, FrozenSet, List, Set, Tuple
    from .lr0node import LR0Node
    from .lr0item import LR0Item
    from .lr0itemset import LR0ItemSet
    from ..log import Logger
