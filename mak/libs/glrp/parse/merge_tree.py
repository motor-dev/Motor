from collections import deque, OrderedDict
from motor_typing import TYPE_CHECKING


class _Tags(object):

    def __init__(self, tags):
        # type: (Dict[int, FrozenSet[str]]) -> None
        self._tags = tags
        self._hash = 0     # len(tags)

    def filter(self, other):
        # type: (_Tags) -> _Tags
        tags = dict()  # type: Dict[int, FrozenSet[str]]
        for index, values in self._tags.items():
            try:
                other_values = other._tags[index]
                values = values & other_values
                if values:
                    tags[index] = values
            except KeyError:
                pass
        return _Tags(tags)

    def create_merge(self, other):
        # type: (_Tags) -> _Tags
        tags = dict(self._tags)
        changed = False
        for index, values in other._tags.items():
            try:
                if not values <= tags[index]:
                    tags[index] = tags[index] | values
                    changed = True
            except KeyError:
                tags[index] = values
                changed = True
        if changed:
            return _Tags(tags)
        else:
            return self

    def is_multiple(self):
        # type: () -> bool
        return len(self._tags) > 1

    def __hash__(self):
        # type: () -> int
        return self._hash

    def __eq__(self, other):
        # type: (Any) -> bool
        return isinstance(other, _Tags) and self._tags == other._tags


class _MergeNode(object):

    ID = 1

    def __init__(self, node, lookahead, tags):
        # type: (LR0Node, bool, _Tags) -> None
        self._node = node
        self._lookahead = lookahead
        self._tags = tags
        self._committed = _Tags({})
        self._predecessors = []    # type: List[_MergeNode]
        self._successors = []      # type: List[_MergeNode]
        self._id = _MergeNode.ID
        _MergeNode.ID += 1

    def commit(self, tags):
        # type: (_Tags) -> None
        queue = [(self, tags)]

        while queue:
            node, tags = queue.pop(-1)
            tags = tags.filter(node._tags)
            committed_tags = node._committed.create_merge(tags)
            if id(committed_tags) != id(node._committed):
                node._committed = committed_tags
                for node in node._predecessors:
                    queue.append((node, committed_tags))

    def update_tags(self, tags):
        # type: (_Tags) -> None
        queue = [(self, tags, tags)]

        while queue:
            node, original_tags, new_tags = queue.pop(-1)
            if id(node._tags) == id(new_tags):
                continue
            if id(node._tags) == id(original_tags):
                node._tags = new_tags
                queue += [(s, original_tags, new_tags) for s in node._successors]
            elif node._tags != new_tags:
                new_tags = node._tags.create_merge(new_tags)
                if id(new_tags) != id(node._tags):
                    original_tags = node._tags
                    node._tags = new_tags
                    queue += [(s, original_tags, node._tags) for s in node._successors]


class _MergeState(object):

    ID = 1

    def __init__(self, entry):
        # type: (Entry) -> None
        self._entry = entry
        self._nodes = {}           # type: Dict[Tuple[LR0Node, bool], _MergeNode]
        self._predecessors = []    # type: List[_MergeState]
        self._successors = []      # type: List[_MergeState]
        self._id = _MergeState.ID
        _MergeState.ID += 1
        item_set = self._entry[0][0]._item_set
        self._state_number = item_set._index
        self._leaf = False
        self._valid = False

    def validate(self):
        # type: () -> None
        queue = [self]

        while queue:
            state = queue.pop(-1)
            if not state._valid:
                state._valid = True
                queue += state._predecessors

    def collect_predecessors(self, lookaheads):
        # type: (Set[int]) -> Tuple[List["Entry"], bool]
        next_nodes = OrderedDict()     # type: OrderedDict[Tuple[LR0Node, bool], _Tags]
        seen = {}                      # type: Dict[Tuple[LR0Node, int], _Tags]

        def backtrack_up(node, la, tags):
            # type: (LR0Node, bool, _Tags) -> bool
            queue = deque([(node, la, tags)])
            has_joined = False

            while queue:
                node, la, tags = queue.popleft()
                try:
                    prev_tags = seen[(node, la)]
                except KeyError:
                    seen[(node, la)] = tags
                else:
                    if prev_tags == tags:
                        continue
                    tags = prev_tags.create_merge(tags)
                    if id(tags) == id(prev_tags):
                        continue
                    seen[(node, la)] = tags
                    # register join
                    has_joined = True
                merge = node._item._merge
                # TODO: merge

                if len(node._predecessors) == 0 and len(node._direct_parents) == 0:
                    self._leaf = True
                else:
                    for parent in node._direct_parents:
                        item = parent._item
                        if la:
                            if not lookaheads.isdisjoint(item._follow):
                                queue.append((parent, False, tags))
                            if -1 in item._follow:
                                queue.append((parent, True, tags))
                        else:
                            queue.append((parent, False, tags))

                    for predecessor in node._predecessors:
                        try:
                            next_nodes[(predecessor, la)] = next_nodes[(predecessor, la)].create_merge(tags)
                        except KeyError:
                            next_nodes[(predecessor, la)] = tags
            return has_joined

        has_joined = False
        for node, la, tags in self._entry:
            has_joined |= backtrack_up(node, la, tags)

        parent_states = OrderedDict()  # type: OrderedDict[int, List[Tuple[LR0Node, bool, _Tags]]]
        for (node, la), tags in next_nodes.items():
            try:
                parent_states[node._item_set._index].append((node, la, tags))
            except KeyError:
                parent_states[node._item_set._index] = [(node, la, tags)]
        return [tuple(entry) for i, entry in parent_states.items()], has_joined

    def refine(self, lookaheads):
        # type: (Set[int]) -> List[Tuple[int, LR0Item]]
        merge_items = []   # type: List[Tuple[int, LR0Item]]
        seen = {}          # type: Dict[Tuple[LR0Node, int], _MergeNode]

        def backtrack_up(node, la, tags, parent_nodes):
            # type: (LR0Node, bool, _Tags, List[_MergeNode]) -> None
            queue = deque([(node, la, tags, parent_nodes)])

            while queue:
                node, la, tags, parent_nodes = queue.popleft()
                try:
                    current_node = seen[(node, la)]
                except KeyError:
                    current_node = _MergeNode(node, la, tags)
                    seen[(node, la)] = current_node

                    for parent in node._direct_parents:
                        item = parent._item
                        if la:
                            if not lookaheads.isdisjoint(item._follow):
                                queue.append((parent, False, current_node._tags, [current_node]))
                            if -1 in item._follow:
                                queue.append((parent, True, current_node._tags, [current_node]))
                        else:
                            queue.append((parent, False, current_node._tags, [current_node]))
                else:
                    current_node.update_tags(tags)
                for parent_node in parent_nodes:
                    if parent_node not in current_node._predecessors:
                        current_node._predecessors.append(parent_node)
                        parent_node._successors.append(current_node)

        for node, la, tags in self._entry:
            backtrack_up(node, la, tags, [])

        for _, merge_node in seen.items():
            for p in merge_node._predecessors:
                if p._tags == merge_node._tags:
                    break
                else:
                    merge_items.append((0, merge_node._node._item))

        return merge_items

    def expand(self, all_states, reduced_states, lookaheads):
        # type: (Dict[Entry, _MergeState], Set[_MergeState], Set[int]) -> None
        next_nodes = OrderedDict()     # type: OrderedDict[Tuple[LR0Node, bool], List[_MergeNode]]
        state = self
        leaves = []                    # type: List[_MergeNode]

        def backtrack_up(state, node, la, tags, parent_nodes):
            # type: (_MergeState, LR0Node, bool, _Tags, List[_MergeNode]) -> None
            queue = deque([(node, la, tags, parent_nodes)])

            while queue:
                node, la, tags, parent_nodes = queue.popleft()
                try:
                    current_node = state._nodes[(node, la)]
                except KeyError:
                    current_node = _MergeNode(node, la, tags)
                    state._nodes[(node, la)] = current_node

                    if len(node._predecessors) == 0 and len(node._direct_parents) == 0:
                        leaves.append(current_node)
                    else:
                        for parent in node._direct_parents:
                            item = parent._item
                            if la:
                                if not lookaheads.isdisjoint(item._follow):
                                    queue.append((parent, False, current_node._tags, [current_node]))
                                if -1 in item._follow:
                                    queue.append((parent, True, current_node._tags, [current_node]))
                            else:
                                queue.append((parent, False, current_node._tags, [current_node]))

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

        parent_nodes = []  # type: List[_MergeNode]
        entries = deque([tuple((self, node, la, tags, parent_nodes) for node, la, tags in self._entry)])
        while entries:
            entry = entries.popleft()
            next_nodes = OrderedDict()
            for state, node, la, tags, parent_nodes in entry:
                backtrack_up(state, node, la, tags, parent_nodes)

            parent_states = OrderedDict() # type: OrderedDict[int, List[Tuple[LR0Node, bool, _Tags, List[_MergeNode]]]]
            for (node, la), parent_nodes in next_nodes.items():
                tags = parent_nodes[0]._tags
                for parent_node in parent_nodes[1:]:
                    tags = tags.create_merge(parent_node._tags)
                try:
                    parent_states[node._item_set._index].append((node, la, tags, parent_nodes))
                except KeyError:
                    parent_states[node._item_set._index] = [(node, la, tags, parent_nodes)]

            for _, nodes in parent_states.items():
                key = tuple((node, la, tags) for node, la, tags, parent_nodes in nodes)
                next_state = all_states[key]
                if next_state in reduced_states:
                    entries.append(
                        tuple((next_state, node, la, tags, parent_nodes) for node, la, tags, parent_nodes in nodes)
                    )

        for leaf in leaves:
            if leaf._tags.is_multiple():
                leaf.commit(leaf._tags)


class MergeTree(object):

    def __init__(self, node_set, lookaheads):
        # type: (List[Tuple[LR0Node, bool, str]], Set[int]) -> None
        self._all_states = set()   # type: Set[_MergeState]
        self._root_state = self._build_tree(node_set, lookaheads)

    def check_resolved(self, name_map, logger):
        # type: (List[str], Logger) -> None
        #merge_node = self._map[root_node._item]
        #if len(merge_node._tags) > 1:
        #    logger.warning('   merge conflicts: [%s]' % ', '.join(merge_node._tags))
        self.print_dot(name_map, logger)
        pass

    def _build_tree(self, node_set, lookaheads):
        # type: (List[Tuple[LR0Node, bool, str]], Set[int]) -> _MergeState
        entry = tuple(
            (node, la, _Tags({i: frozenset([symbol])})) for i, (node, la, symbol) in enumerate(node_set)
        )                                                                                                  # type: Entry
        root = _MergeState(entry)
        states = {entry: root}
        queue = [root]
        leaves = []

        interesting_states = []    # type: List[_MergeState]
        important_states = {
            0: OrderedDict(),
            1: OrderedDict(),
            2: OrderedDict()
        }                          # type: Dict[int, OrderedDict[LR0Item, List[_MergeState]]]
        while queue:
            state = queue.pop(0)
            entries, merges = state.collect_predecessors(lookaheads)
            if state._leaf:
                leaves.append(state)
            if merges:
                interesting_states.append(state)

            for entry in entries:
                try:
                    new_state = states[entry]
                except KeyError:
                    new_state = _MergeState(entry)
                    states[entry] = new_state
                    queue.append(new_state)
                if new_state not in state._successors:
                    state._successors.append(new_state)
                    new_state._predecessors.append(state)

        for leaf in leaves:
            leaf.validate()

        for state in interesting_states:
            if state._valid:
                for merge_type, merge_item in state.refine(lookaheads):
                    d = important_states[merge_type]
                    try:
                        d[merge_item].append(state)
                    except KeyError:
                        d[merge_item] = [state]

        # go through all important states, find shortest path to top & bottom
        downstream_states = set()  # type: Set[_MergeState]
        for index in 2, 1, 0:
            for item, state_list in important_states[index].items():
                for state in state_list:
                    if state in self._all_states:
                        break
                else:
                    for origin_state in state_list:
                        if origin_state._valid:
                            seen = set([origin_state])
                            queue2 = deque([(origin_state, [origin_state])])
                            while queue2:
                                state, path = queue2.popleft()
                                if state in self._all_states:
                                    self._all_states.update(path)
                                    break
                                if state._leaf:
                                    self._all_states.update(path)
                                    break
                                for successor in state._successors:
                                    if successor in seen:
                                        continue
                                    seen.add(successor)
                                    queue2.append((successor, path + [successor]))

                            queue2 = deque([(origin_state, [origin_state])])
                            while queue2:
                                state, path = queue2.popleft()
                                if state in downstream_states:
                                    downstream_states.update(path)
                                    break
                                if not state._predecessors:
                                    assert state == root
                                    downstream_states.update(path)
                                    break
                                for predecessor in state._predecessors:
                                    if predecessor in seen:
                                        continue
                                    seen.add(predecessor)
                                    queue2.append((predecessor, path + [predecessor]))
                            self._all_states.update(downstream_states)
                            break

        # expand all states
        root.expand(states, self._all_states, lookaheads)
        return root

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

        for state in self._all_states:
            out_stream.info('     subgraph cluster_%d {' % (state._id))
            out_stream.info('       label="State %d"; style="rounded";' % (state._state_number))

            for (node, la), merge_node in state._nodes.items():
                if len(merge_node._committed._tags) > 0:
                    all_tags = set()   # type: Set[str]
                    for tlist in merge_node._committed._tags.values():
                        all_tags.update(tlist)

                    color = ':'.join([get_color(tag) for tag in all_tags])
                    border_color = ''
                    out_stream.info(
                        '       %d[label="%s[%s]\\n%s"]%s[fillcolor="%s"];' % (
                            merge_node._id, name_map[node._item._symbol], ', '.join(all_tags),
                            node._item.to_short_string(name_map), border_color, color
                        )
                    )

            out_stream.info('     }')

        for state in self._all_states:
            for merge_node in state._nodes.values():
                if len(merge_node._committed._tags) > 0:
                    for predecessor in merge_node._predecessors:
                        if len(predecessor._committed._tags) > 0:
                            out_stream.info('     %d->%d;' % (predecessor._id, merge_node._id))
        out_stream.info('   }')


if TYPE_CHECKING:
    from motor_typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple
    Entry = Tuple[Tuple[LR0Node, bool, _Tags], ...]
    from .lr0node import LR0Node
    from .lr0item import LR0Item
    from .lr0itemset import LR0ItemSet
    from ..log import Logger
