from collections import deque, OrderedDict
from typing import TYPE_CHECKING


class _Tags(object):

    def __init__(self, indices, tags):
        # type: (int, FrozenSet[str]) -> None
        self._tags = tags
        self._indices = indices

    def create_merge(self, other):
        # type: (_Tags) -> _Tags
        new_indices = other._indices & ~self._indices
        changed = new_indices != 0 or not other._tags <= self._tags
        if changed:
            return _Tags(self._indices | other._indices, self._tags | other._tags)
        else:
            return self

    def __hash__(self):
        # type: () -> int
        return self._indices

    def __eq__(self, other):
        # type: (Any) -> bool
        return isinstance(other, _Tags) and self._indices == other._indices and self._tags == other._tags


class _MergeNode(object):
    ID = 1

    def __init__(self, state, node, lookahead, tags):
        # type: (_MergeState, LR0Node, bool, _Tags) -> None
        self._state = state
        self._node = node
        self._lookahead = lookahead
        self._tags_entry = tags
        self._committed = True  # TODO!
        if node._item._index == 0:
            self._merge_map = node._item._last._merge_map
            self._merge_set = node._item._last._merge_set
        else:
            self._merge_map = {}
            self._merge_set = frozenset()
        self._merge_registry = {}  # type: Dict[str, str]
        self._merge_object = None  # type: Optional[Grammar.Merge]
        self._predecessors = []  # type: List[_MergeNode]
        self._successors = []  # type: List[_MergeNode]
        self._id = _MergeNode.ID
        self._tags_exit = self._merge(tags)
        _MergeNode.ID += 1

    def _merge(self, tags):
        # type: (_Tags) -> _Tags
        # return tags
        if self._merge_map and not self._merge_set.isdisjoint(tags._tags):

            def _get_tag(tag):
                # type: (str) -> str
                try:
                    result = self._merge_map[tag]
                except KeyError:
                    return tag
                else:
                    assert self._merge_object is None or self._merge_object == result
                    self._merge_object = result
                    self._merge_registry[tag] = result._result
                    self._state._add_merge(self, result)
                    result.use(tag)
                    return result._result

            tags = _Tags(tags._indices, frozenset((_get_tag(x) for x in tags._tags)))
            assert self._merge_object is not None
            self._state._add_merge_result(self._merge_object, tags)
            return tags
        else:
            return tags

    def commit(self):
        # type: () -> None
        queue = [self]

        while queue:
            node = queue.pop(-1)
            if not node._committed:
                node._committed = True
                queue += node._predecessors

    def update_tags(self, tags):
        # type: (_Tags) -> None
        queue = [(self, self._tags_entry, tags)]

        while queue:
            node, prev_tags, merge_tags = queue.pop(-1)
            if id(prev_tags) == id(merge_tags):
                continue
            new_tags = node._tags_entry.create_merge(merge_tags)
            if id(new_tags) == id(node._tags_entry):
                continue
            original_tags = node._tags_exit
            node._tags_entry = new_tags
            node._tags_exit = node._merge(new_tags)
            queue += [(s, original_tags, node._tags_exit) for s in node._successors]


class _MergeState(object):
    ID = 1

    def __init__(self, entry):
        # type: (Entry) -> None
        self._entry = entry
        self._entry_indices = 0
        for e in entry:
            self._entry_indices |= e[3]._indices
        self._nodes = {}  # type: Dict[Tuple[LR0Node, bool, bool], _MergeNode]
        self._merge_registry = {}  # type: Dict[Grammar.Merge, List[_MergeNode]]
        self._merge_result = {}  # type: Dict[Grammar.Merge, _Tags]
        self._node_merge_registry = {}  # type: Dict[_MergeNode, Grammar.Merge]
        self._predecessors = []  # type: List[_MergeState]
        self._successors = []  # type: List[_MergeState]
        self._id = _MergeState.ID
        _MergeState.ID += 1
        item_set = self._entry[0][0]._item_set
        self._state_number = item_set._index
        self._leaf = False
        self._leaf_nodes = []  # type: List[_MergeNode]
        self._valid = False
        self._important_items = {}  # type: Dict[LR0Node, int]
        self._error_nodes = []  # type: List[Tuple[_MergeNode, str]]

    def validate(self):
        # type: () -> None
        queue = [self]

        while queue:
            state = queue.pop(-1)
            if not state._valid:
                state._valid = True
                queue += state._predecessors

    def _add_merge(self, node, merge):
        # type: (_MergeNode, Grammar.Merge) -> None
        try:
            self._merge_registry[merge].append(node)
        except KeyError:
            self._merge_registry[merge] = [node]
        assert node not in self._node_merge_registry

    def _add_merge_result(self, merge, tags):
        # type: (Grammar.Merge, _Tags) -> None
        try:
            self._merge_result[merge] = self._merge_result[merge].create_merge(tags)
        except KeyError:
            self._merge_result[merge] = tags

    def collect_predecessors(self, lookahead):
        # type: (int) -> Tuple[List["Entry"], bool]
        next_nodes = OrderedDict()  # type: OrderedDict[Tuple[LR0Node, bool], _Tags]
        seen = {}  # type: Dict[Tuple[LR0Node, bool, bool], _Tags]

        def backtrack_up(node, la, reduction, tags):
            # type: (LR0Node, bool, bool, _Tags) -> bool
            queue = deque([(node, la, reduction, tags)])
            has_joined = False

            while queue:
                node, la, reduction, tags = queue.popleft()

                if node._item in node._item_set._discarded:
                    if lookahead in node._item_set._discarded[node._item]:
                        continue

                try:
                    prev_tags = seen[(node, la, reduction)]
                except KeyError:
                    seen[(node, la, reduction)] = tags
                else:
                    if prev_tags == tags:
                        continue
                    tags = prev_tags.create_merge(tags)
                    if id(tags) == id(prev_tags):
                        continue
                    seen[(node, la, reduction)] = tags
                    # register join
                    has_joined = True

                if node._item._index == 0 and not node._item._last._merge_set.isdisjoint(tags._tags):
                    merge_map = node._item._last._merge_map

                    def _get_tag(tag):
                        # type: (str) -> str
                        try:
                            result = merge_map[tag]
                        except KeyError:
                            return tag
                        else:
                            result.use(tag)
                            return result._result

                    tags = _Tags(tags._indices, frozenset((_get_tag(t) for t in tags._tags)))

                if len(node._predecessors) == 0 and len(node._direct_parents) == 0:
                    self._leaf = True
                else:
                    for parent in node._direct_parents:
                        item = parent._item
                        if la:
                            if lookahead in item._follow:
                                queue.append((parent, False, True, tags))
                            if -1 in item._follow:
                                queue.append((parent, True, True, tags))
                        else:
                            queue.append((parent, False, True, tags))

                    for predecessor in node._predecessors:
                        try:
                            next_nodes[(predecessor, la)] = next_nodes[(predecessor, la)].create_merge(tags)
                        except KeyError:
                            next_nodes[(predecessor, la)] = tags
            return has_joined

        has_joined = False
        for node, la, reduction, tags in self._entry:
            has_joined |= backtrack_up(node, la, reduction, tags)

        parent_states = OrderedDict()  # type: OrderedDict[int, List[Tuple[LR0Node, bool, bool, _Tags]]]
        for (node, la), tags in next_nodes.items():
            try:
                parent_states[node._item_set._index].append((node, la, False, tags))
            except KeyError:
                parent_states[node._item_set._index] = [(node, la, False, tags)]
        return [tuple(entry) for i, entry in parent_states.items()], has_joined

    def refine(self, lookahead):
        # type: (int) -> None
        seen = {}  # type: Dict[Tuple[LR0Node, bool, bool], _MergeNode]

        def backtrack_up(node, la, reduction, tags, parent_nodes):
            # type: (LR0Node, bool, bool, _Tags, List[_MergeNode]) -> None
            queue = deque([(node, la, reduction, tags, parent_nodes)])

            while queue:
                node, la, reduction, tags, parent_nodes = queue.popleft()

                if node._item in node._item_set._discarded:
                    if lookahead in node._item_set._discarded[node._item]:
                        continue

                if parent_nodes:
                    tags = parent_nodes[0]._tags_exit
                    for p in parent_nodes[1:]:
                        tags = tags.create_merge(p._tags_exit)

                try:
                    current_node = seen[(node, la, reduction)]
                except KeyError:
                    current_node = _MergeNode(self, node, la, tags)
                    seen[(node, la, reduction)] = current_node

                    for parent in node._direct_parents:
                        item = parent._item
                        if la:
                            if lookahead in item._follow:
                                queue.append((parent, False, True, tags, [current_node]))
                            if -1 in item._follow:
                                queue.append((parent, True, True, tags, [current_node]))
                        else:
                            queue.append((parent, False, True, tags, [current_node]))
                else:
                    current_node.update_tags(tags)
                for parent_node in parent_nodes:
                    if parent_node not in current_node._predecessors:
                        current_node._predecessors.append(parent_node)
                        parent_node._successors.append(current_node)

        for node, la, reduction, tags in self._entry:
            backtrack_up(node, la, reduction, tags, [])

        for (node, la, _), merge_node in seen.items():
            for p in merge_node._predecessors:
                if p != merge_node and id(p._tags_exit) != id(
                        merge_node._tags_entry
                ) and p._tags_exit._indices != merge_node._tags_entry._indices and p._tags_exit._tags != merge_node._tags_entry._tags:
                    self._important_items[node] = 0
                    break
        for (node, _, _), merge_node in seen.items():
            count = 0
            for p in merge_node._predecessors:
                if p._tags_exit._indices != merge_node._tags_entry._indices:
                    count += len(p._merge_registry) > 0
            if count > 1:
                for p in merge_node._predecessors:
                    if p._tags_exit._indices != merge_node._tags_entry._indices and len(p._merge_registry) > 0:
                        self._important_items[p._node] = 2

        for (node, _, _), merge_node in seen.items():
            if node._item._no_merge_warning:
                continue
            if len(merge_node._predecessors) > 1:
                for p in merge_node._predecessors:
                    if p._merge_object is not None:
                        tags = self._merge_result[p._merge_object]
                    else:
                        tags = p._tags_exit
                    # if tags != merge_node._tags_entry:
                    #    self._error_nodes.append((merge_node, 'weird'))
                    #    self._important_items[node] = 1
                    #    break

    def expand(self, all_states, reduced_states, lookahead):
        # type: (Dict[Entry, _MergeState], Set[_MergeState], int) -> None
        next_nodes = OrderedDict()  # type: OrderedDict[Tuple[LR0Node, bool], List[_MergeNode]]
        state = self
        leaves = []  # type: List[_MergeNode]
        _MergeNode.ID = 0
        _MergeState.ID = 0

        def backtrack_up(state, node, la, reduction, tags, parent_nodes):
            # type: (_MergeState, LR0Node, bool, bool, _Tags, List[_MergeNode]) -> None
            queue = deque([(node, la, reduction, tags, parent_nodes)])

            while queue:
                node, la, reduction, tags, parent_nodes = queue.popleft()

                if node._item in node._item_set._discarded:
                    if lookahead in node._item_set._discarded[node._item]:
                        continue

                if parent_nodes:
                    tags = parent_nodes[0]._tags_exit
                    for p in parent_nodes[1:]:
                        tags = tags.create_merge(p._tags_exit)

                try:
                    current_node = state._nodes[(node, la, reduction)]
                except KeyError:
                    current_node = _MergeNode(state, node, la, tags)
                    state._nodes[(node, la, reduction)] = current_node

                    if len(node._predecessors) == 0 and len(node._direct_parents) == 0:
                        leaves.append(current_node)
                        if len(current_node._tags_entry._tags) > 1:
                            state._error_nodes.append((current_node, 'split not fully resolved'))
                    else:
                        for parent in node._direct_parents:
                            item = parent._item
                            if la:
                                if lookahead in item._follow:
                                    queue.append((parent, False, True, tags, [current_node]))
                                if -1 in item._follow:
                                    queue.append((parent, True, True, tags, [current_node]))
                            else:
                                queue.append((parent, False, True, tags, [current_node]))

                        if node._predecessors:
                            state._leaf_nodes.append(current_node)
                            for predecessor in node._predecessors:
                                try:
                                    next_nodes[(predecessor, la)].append(current_node)
                                except KeyError:
                                    next_nodes[(predecessor, la)] = [current_node]
                else:
                    current_node.update_tags(tags)
                for parent_node in parent_nodes:
                    if parent_node not in current_node._predecessors:
                        current_node._predecessors.append(parent_node)
                        parent_node._successors.append(current_node)

            for current_node in state._nodes.values():
                if current_node._node._item._no_merge_warning:
                    continue
                if len(current_node._tags_entry._tags) > 1:
                    for p in current_node._predecessors:
                        if current_node._tags_entry._tags != p._tags_exit._tags:
                            state._error_nodes.append((current_node, 'missing merge annotation'))
                            break

        parent_nodes = []  # type: List[_MergeNode]
        entries = deque(
            [tuple((self, node, la, reduction, tags, parent_nodes) for node, la, reduction, tags in self._entry)]
        )
        while entries:
            entry = entries.popleft()
            next_nodes = OrderedDict()
            for state, node, la, reduction, tags, parent_nodes in entry:
                backtrack_up(state, node, la, reduction, tags, parent_nodes)

            parent_states = OrderedDict()  # type: OrderedDict[int, List[Tuple[LR0Node, bool, _Tags, List[_MergeNode]]]]
            for (node, la), parent_nodes in next_nodes.items():
                tags = parent_nodes[0]._tags_exit
                try:
                    parent_states[node._item_set._index].append((node, la, tags, parent_nodes))
                except KeyError:
                    parent_states[node._item_set._index] = [(node, la, tags, parent_nodes)]
            if state._leaf:
                leaves += state._leaf_nodes
            else:
                for _, nodes in parent_states.items():
                    key = tuple((node, la, False, tags) for node, la, tags, parent_nodes in nodes)
                    next_state = all_states[key]
                    if next_state in reduced_states:
                        entries.append(
                            tuple(
                                (next_state, node, la, False, tags, parent_nodes)
                                for node, la, tags, parent_nodes in nodes
                            )
                        )

        for leaf in leaves:
            if bin(leaf._tags_exit._indices).count("1") > 1:
                leaf.commit()


class MergeTree(object):

    def __init__(self, node_set, lookahead):
        # type: (List[Tuple[LR0Node, bool, str]], int) -> None
        self._all_states = set()  # type: Set[_MergeState]
        self._paths = {}  # type: Dict[_MergeState, Set[_MergeState]]
        self._error_nodes = []  # type: List[_MergeNode]
        self._root_state = self._build_tree(node_set, lookahead)

    def check_resolved(self, name_map, error_log, file_log):
        # type: (List[str], Logger, Logger) -> None
        for leaf_state, graph in self._paths.items():
            errors = {}  # type: Dict[Tuple[int, str], List[_MergeNode]]

            seen = set()
            for state in graph:
                for error_node, message in state._error_nodes:
                    for parent in error_node._predecessors:
                        if (parent._node, parent._tags_exit, message) not in seen:
                            seen.add((parent._node, parent._tags_exit, message))
                            try:
                                errors[(parent._node._item._symbol, message)].append(parent)
                            except KeyError:
                                errors[(parent._node._item._symbol, message)] = [parent]
            if errors:
                for (nonterminal, message), error_list in sorted(errors.items()):
                    error_log.warning('%s at nonterminal %s' % (message, name_map[nonterminal]))
                    for error in error_list:
                        error_log.diagnostic(
                            error._node._item.rule._filename, error._node._item.rule._lineno,
                            '[%s] %s' % (', '.join(error._tags_exit._tags), error._node._item.to_string(name_map))
                        )
                self.print_dot(graph, name_map, file_log)

    def _gather_essential_states(self, interesting_states, lookahead):
        # type: (List[_MergeState], int) -> Set[_MergeState]
        result = set()  # type: Set[_MergeState]
        important_items = {}  # type: Dict[Tuple[int, LR0Item], List[_MergeState]]

        def filter_items(from_state):
            # type: (List[_MergeState]) -> None
            for state in from_state:
                for node, t in state._important_items.items():
                    try:
                        del important_items[(t, node._item)]
                    except KeyError:
                        pass

        for state in interesting_states:
            if state._valid:
                state.refine(lookahead)
                for node, t in state._important_items.items():
                    try:
                        important_items[(t, node._item)].append(state)
                    except KeyError:
                        important_items[(t, node._item)] = [state]

        # go through all important states, find shortest path to top & bottom
        while important_items:
            x = sorted(important_items.items(), key=lambda x: len(x[1]))
            origin_state = x[0][1][0]

            # compute the shortest paths that goes from the root to a leaf that traverses this state
            seen = set([origin_state])
            queue = deque([(origin_state, [origin_state])])
            while queue:
                state, path = queue.popleft()
                if state._state_number == 0:
                    result.update(path)
                    break
                for successor in state._successors:
                    if successor in seen:
                        continue
                    seen.add(successor)
                    queue.append((successor, path + [successor]))

            queue = deque([(origin_state, path[::-1])])
            seen = set([origin_state])
            while queue:
                state, path = queue.popleft()
                if not state._predecessors:
                    # for each other state, remove all items that will be treated by this state
                    filter_items(path)
                    result.update(path)
                    try:
                        self._paths[path[0]].update(path)
                    except KeyError:
                        self._paths[path[0]] = set(path)
                    break
                for predecessor in state._predecessors:
                    if predecessor in seen:
                        continue
                    seen.add(predecessor)
                    queue.append((predecessor, path + [predecessor]))

        return result

    def _build_tree(self, node_set, lookahead):
        # type: (List[Tuple[LR0Node, bool, str]], int) -> _MergeState
        def get_index(i, tag):
            # type: (int, str) -> int
            for j, (_, _, symbol) in enumerate(node_set):
                if tag == symbol:
                    return 1 << j
            assert False

        entry = tuple(
            (node, la, False, _Tags(get_index(i, symbol), frozenset((symbol,))))
            for i, (node, la, symbol) in enumerate(node_set)
        )

        root = _MergeState(entry)
        states = {entry: root}
        queue = [root]
        leaves = []
        interesting_states = []  # type: List[_MergeState]

        while queue:
            state = queue.pop(0)
            entries, merges = state.collect_predecessors(lookahead)
            if merges:
                interesting_states.append(state)
            if state._leaf:
                leaves.append(state)
            else:
                for entry in entries:
                    for e in entry:
                        if e[3]._indices != state._entry_indices or len(e[3]._tags) > 1:
                            try:
                                new_state = states[entry]
                            except KeyError:
                                new_state = _MergeState(entry)
                                states[entry] = new_state
                                queue.append(new_state)
                            if new_state not in state._successors:
                                state._successors.append(new_state)
                                new_state._predecessors.append(state)
                            break
                    else:
                        state._leaf = True
                        leaves.append(state)

        for leaf in leaves:
            leaf.validate()

        # compute a restricted set of states that contains all essential ones
        self._all_states = self._gather_essential_states(interesting_states, lookahead)

        # expand all states
        root.expand(states, self._all_states, lookahead)
        return root

    def print_dot(self, graph, name_map, out_stream):
        # type: (Set[_MergeState], List[str], Logger) -> None
        out_stream.info('')
        out_stream.info('   digraph MergeTree {')
        out_stream.info('     node[style="filled,striped,rounded",shape="box"];')
        colors = [
            'aquamarine',
            'burlywood',
            'coral',
            'darkgoldenrod1',
            'darkolivegreen1',
            'darkslategray2',
            'deepskyblue',
            'gray',
            'khaki1',
            'lightpink1',
            'mistyrose',
            'palegreen1',
            'rosybrown2',
            'thistle',
            'wheat1',
            'chartreuse2',
            'darkorchid1',
            'gainsboro',
            'lightcyan3',
            'peachpuff',
            'seashell3',
            'slategray1',
            'rosybrown1',
        ]
        tags = {}  # type: Dict[str, str]
        borders = (',color=red,penwidth=3', ',color=blue,penwidth=3', ',color=green,penwidth=3', '')

        def get_color(tag):
            # type: (str) -> str
            try:
                return tags[tag]
            except KeyError:
                result = colors[len(tags)]
                tags[tag] = result
                return result

        for state in sorted(graph, key=lambda x: x._id):
            out_stream.info('     subgraph cluster_%d {' % (state._id))
            out_stream.info(
                '       label="State %d"; style="rounded"; labeljust="l"; bgcolor="lightgray"' % (state._state_number)
            )

            node_index = {}  # type: Dict[str, Tuple[Set[str], List[_MergeNode]]]
            for (node, _, _), merge_node in state._nodes.items():
                if merge_node._committed:
                    for origin, target in merge_node._merge_registry.items():
                        try:
                            s, n = node_index[target]
                        except KeyError:
                            node_index[target] = (set((origin,)), [merge_node])
                        else:
                            s.add(origin)
                            n.append(merge_node)

            for merge_result, (tag_set, merge_nodes) in node_index.items():
                out_stream.info('       subgraph cluster_%d_%s {' % (state._id, merge_result))
                out_stream.info(
                    '         label="%s \u21d2 %s"; style="rounded,filled"; color="lightpink"; labeljust="l";' %
                    (', '.join(sorted(tag_set)), merge_result)
                )
                for merge_node in merge_nodes:
                    color = ':'.join(sorted([get_color(tag) for tag in merge_node._tags_entry._tags]))
                    border_color = borders[state._important_items.get(node, 3)]
                    out_stream.info(
                        '         %d[label="%s[%s]\\n%s"%s,fillcolor="%s"];' % (
                            merge_node._id, name_map[merge_node._node._item._symbol], ', '.join(
                                merge_node._tags_entry._tags
                            ), merge_node._node._item.to_short_string(name_map), border_color, color
                        )
                    )
                out_stream.info('       }')

            for (node, la, _), merge_node in state._nodes.items():
                if merge_node._committed and len(merge_node._merge_registry) == 0:
                    color = ':'.join(sorted([get_color(tag) for tag in merge_node._tags_entry._tags]))
                    border_color = borders[state._important_items.get(node, 3)]
                    out_stream.info(
                        '       %d[label="%s[%s]\\n%s"%s,fillcolor="%s"];' % (
                            merge_node._id, name_map[node._item._symbol], ', '.join(merge_node._tags_entry._tags),
                            node._item.to_short_string(name_map), border_color, color
                        )
                    )

            out_stream.info('     }')

        for state in graph:
            for merge_node in state._nodes.values():
                if merge_node._committed:
                    for predecessor in merge_node._predecessors:
                        if predecessor._state in graph and predecessor._committed:
                            out_stream.info('     %d->%d;' % (predecessor._id, merge_node._id))
        out_stream.info('   }')
        out_stream.info('')
        out_stream.info('')


if TYPE_CHECKING:
    from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

    Indices = int
    Entry = Tuple[Tuple[LR0Node, bool, bool, _Tags], ...]
    from .lr0node import LR0Node
    from .lr0item import LR0Item
    from .grammar import Grammar
    from ..log import Logger
