from motor_typing import TYPE_CHECKING


class MergeTree(object):

    def __init__(self, node_set):
        # type: (List[Tuple[LR0Node, Set[int], str]]) -> None
        self._map = {}     # type: Dict[LR0Node, MergeNode]

        self._add_nodes(node_set)
        for node, _, tag in node_set:
            self._map[node].add_tag(tag)

    def check_resolved(self, root_node, name_map, logger):
        # type: (LR0Node, List[str], Logger) -> None
        #merge_node = self._map[root_node._item]
        #if len(merge_node._tags) > 1:
        #    logger.warning('   merge conflicts: [%s]' % ', '.join(merge_node._tags))
        self.print_dot(name_map, logger)
        pass

    def backtrack_up(self, node, path, lookaheads, seen):
        # type: (LR0Node, List[Tuple[LR0Node, bool]], Set[int], Set[Tuple[LR0Node, bool]]) -> List[Tuple[LR0Node, List[Tuple[LR0Node, bool]], Set[int], int]]
        queue = [(node, path, lookaheads)]
        result = []    # type: List[Tuple[LR0Node, List[Tuple[LR0Node, bool]], Set[int], int]]

        while queue:
            node, path, lookaheads = queue.pop(0)

            for parent in node._direct_parents:
                if (parent, len(lookaheads) > 0) in seen:
                    continue
                seen.add((parent, len(lookaheads) > 0))
                item = parent._item
                if lookaheads:
                    if not lookaheads.isdisjoint(item._follow):
                        queue.append((parent, path, set()))
                    if -1 in item._follow:
                        queue.append((parent, path, lookaheads))
                else:
                    queue.append((parent, path, lookaheads))
            for predecessor in node._predecessors:
                assert node._predecessor_lookahead is not None
                result.append(
                    (predecessor, path + [(predecessor, len(lookaheads) > 0)], lookaheads, node._predecessor_lookahead)
                )

        return result

    def backtrack_to_target(self, node, path, lookaheads, seen, target):
        # type: (LR0Node, List[Tuple[LR0Node, bool]], Set[int], Set[Tuple[LR0Node, bool]], LR0Node) -> List[List[Tuple[LR0Node, bool]]]
        queue = [(node, path, lookaheads)]
        result = []    # type: List[List[Tuple[LR0Node, bool]]]

        while queue:
            node, path, lookaheads = queue.pop(0)

            for parent in node._direct_parents:
                if parent == target:
                    result.append(path + [(parent, False)])
                if (parent, False) in seen:
                    continue
                seen.add((parent, False))
                item = parent._item
                if lookaheads:
                    if not lookaheads.isdisjoint(item._follow):
                        queue.append((parent, path, set()))
                    if -1 in item._follow:
                        queue.append((parent, path, lookaheads))
                else:
                    queue.append((parent, path, lookaheads))
        return result

    def _add_nodes(self, node_set):
        # type: (List[Tuple[LR0Node, Set[int], str]]) -> None
        for node, _, _ in node_set:
            self._map[node] = MergeNode(node._item)

        all_paths = [
            (node, lookaheads, []) for node, lookaheads, _ in node_set
        ]                                                              # type: List[Tuple[LR0Node, Set[int], List[List[Tuple[LR0Node, bool]]]]]

        lst = []   # type: List[List[Tuple[LR0Node, List[Tuple[LR0Node, bool]], Set[int], Set[Tuple[LR0Node, bool]]]]]
        for node, lookaheads, _ in node_set:
            lst.append([(node, [(node, len(lookaheads) > 0)], lookaheads, set())])
        queue = [(lst, node_set[0][0]._item_set._index)]

        while queue:
            path_list, state = queue.pop(0)

            if state == 0:
                for index, paths in enumerate(path_list):
                    for node, path, lookahead, seen in paths:
                        root_node = list(node._item_set._core)[0]
                        all_paths[index][2].extend(self.backtrack_to_target(node, path, lookahead, seen, root_node))

            states = {
            }              # type: Dict[Tuple[int, int], List[List[Tuple[LR0Node, List[Tuple[LR0Node, bool]], Set[int], Set[Tuple[LR0Node, bool]]]]]]
            for index, paths in enumerate(path_list):
                for node, path, lookahead, seen in paths:
                    predecessor_list = self.backtrack_up(node, path, lookahead, seen)
                    for predecessor, predecessor_path, lookaheads, consumed_token in predecessor_list:
                        try:
                            predecessors = states[(predecessor._item_set._index, consumed_token)]
                        except KeyError:
                            predecessors = [[] for _ in path_list]
                            states[(predecessor._item_set._index, consumed_token)] = predecessors
                        predecessors[index].append((predecessor, predecessor_path, lookaheads, seen))

            for (state, consumed_token), nodes_list in states.items():
                count = 0
                for nodes in nodes_list:
                    if len(nodes) > 0:
                        count += 1
                if count > 1:
                    queue.append((nodes_list, state))

        self._build_tree(all_paths)

    def _build_tree(self, paths):
        # type: (List[Tuple[LR0Node, Set[int], List[List[Tuple[LR0Node, bool]]]]]) -> None
        states = {}    # type: Dict[int, Tuple[Set[int], List[Tuple[LR0Node, bool]], List[Tuple[LR0Node, bool]]]]
        for _, lookaheads, path_list in paths:
            for path in path_list:
                head, la = path[0]
                for tail, la_tail in path[1:]:
                    state = head._item_set._index
                    try:
                        states[state][1].append((head, la))
                        states[state][2].append((tail, la_tail))
                    except KeyError:
                        states[state] = (lookaheads, [(head, la)], [(tail, la_tail)])
                    head = tail
                    la = la_tail

        for _, (lookaheads, heads, dest) in states.items():
            targets = set(dest)
            for node, _ in heads + dest:
                if node not in self._map:
                    self._map[node] = MergeNode(node._item)
            item_set = heads[0][0]._item_set

            queue = list(targets)
            seen = set()
            while queue:
                node, la = queue.pop(0)
                if (node, la) in seen:
                    continue
                seen.add((node, la))
                if node._item_set != item_set:
                    assert node._successor is not None
                    targets.add((node._successor, la))
                    queue.append((node._successor, la))
                else:
                    item = node._item
                    if la:
                        if -1 in item._follow:
                            for child in node._direct_children:
                                targets.add((child, True))
                                queue.append((child, True))
                    else:
                        if not lookaheads.isdisjoint(item._follow):
                            for child in node._direct_children:
                                targets.add((child, True))
                                queue.append((child, True))
                        for child in node._direct_children:
                            targets.add((child, False))
                            queue.append((child, False))

            seen = set()
            queue = list(heads)
            while queue:
                node, la = queue.pop(0)
                merge_node = self._map[node]
                assert ((node, la)) in targets
                if (node, la) in seen:
                    continue
                seen.add((node, la))

                for parent_node in node._direct_parents:
                    item = parent_node._item
                    if (parent_node, la) in targets:
                        try:
                            parent_merge_node = self._map[parent_node]
                        except KeyError:
                            parent_merge_node = MergeNode(item)
                            self._map[parent_node] = parent_merge_node
                        merge_node._parents.add(parent_merge_node)
                        queue.append((parent_node, la))
                    if la:
                        if (parent_node, False) in targets:
                            try:
                                parent_merge_node = self._map[parent_node]
                            except KeyError:
                                parent_merge_node = MergeNode(item)
                                self._map[parent_node] = parent_merge_node
                            merge_node._parents.add(parent_merge_node)
                            queue.append((parent_node, False))
                for predecessor in node._predecessors:
                    if (predecessor, la) in targets:
                        try:
                            parent_merge_node = self._map[predecessor]
                        except KeyError:
                            parent_merge_node = MergeNode(predecessor._item)
                            self._map[predecessor] = parent_merge_node
                        merge_node._parents.add(parent_merge_node)

    def print_dot(self, name_map, out_stream):
        # type: (List[str], Logger) -> None
        out_stream.info('   digraph MergeTree {')
        out_stream.info('      node[style=filled][shape=box];')
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

        for node, merge_node in self._map.items():
            color = ':'.join([get_color(tag) for tag in merge_node._tags])
            out_stream.info(
                '      %d[label="%s[%s]\\n%s"][fillcolor="%s"];' % (
                    id(merge_node), name_map[node._item._symbol
                                             ], ', '.join(merge_node._tags), node._item.to_short_string(name_map), color
                )
            )
        for item, merge_node in self._map.items():
            for parent in merge_node._parents:
                if merge_node._tags.difference(parent._tags):
                    out_stream.info('      %d->%d[color=red];' % (id(parent), id(merge_node)))
                else:
                    out_stream.info('      %d->%d;' % (id(parent), id(merge_node)))
        out_stream.info('   }')


class MergeNode(object):

    def __init__(self, item):
        # type: (LR0Item) -> None
        self._item = item
        self._tags = set()     # type: Set[str]
        self._parents = set()  # type: Set[MergeNode]

    def add_tag(self, tag):
        # type: (str) -> None
        if tag not in self._tags:
            self._tags.add(tag)
            if self._item._index == 0:
                for result, merged_tags in self._item._last._merge:
                    if tag in merged_tags:
                        tag = result
            for parent in self._parents:
                parent.add_tag(tag)


if TYPE_CHECKING:
    from motor_typing import Dict, List, Optional, Set, Tuple
    from .lr0node import LR0Node
    from .lr0item import LR0Item
    from ..log import Logger
