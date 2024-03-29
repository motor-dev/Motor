from .lr0itemset import LR0ItemSet
from .lr0node import LR0Node
from .lr0path import LR0PathItem
from .lr0dominancenode import LR0DominanceSet
from .merge_tree import MergeTree
from typing import TYPE_CHECKING
import os
import sys


def get_terminal_size():
    # type: () -> Tuple[int, int]
    env = os.environ

    def ioctl_GWINSZ(fd):
        # type: (int) -> Optional[Tuple[str, str]]
        try:
            import fcntl, termios, struct
            cr = struct.unpack('HHHH', fcntl.ioctl(fd, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0)))
        except Exception as e:
            return None
        return str(cr[0]), str(cr[1])

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', '25'), env.get('COLUMNS', '80'))
    return int(cr[0]), int(cr[1])


class LALRTable(object):

    def __init__(self, action_table, goto_table):
        # type: (List[Dict[int, Tuple[Tuple[int, Optional[str]],...]]], List[Dict[int, int]]) -> None
        self._action_table = action_table
        self._goto_table = goto_table


def _find_merge_points(conflict_list, lookahead, name_map, logger, error_log):
    # type: (List[Tuple[LR0Node, bool, str]], int, List[str], Logger, Logger) -> None
    merge_tree = MergeTree(conflict_list, lookahead)
    merge_tree.check_resolved(name_map, error_log, logger)
    pass


def _log(title, conflict_paths, out, name_map):
    # type: (Text, List[LR0Path], Logger, List[str]) -> None
    seen = set([])
    if conflict_paths:
        count = len(set(conflict_paths))
        out.info(u'   %s', title)
        out.info(u'   \u256d\u2574')
        for path in conflict_paths:
            if path in seen:
                continue
            count -= 1
            seen.add(path)
            strings = path.to_string(name_map)
            for s in strings:
                out.info(u'   \u2502 %s', s)
            if count == 0:
                out.info(u'   \u2570\u2574')
            else:
                out.info(u'   \u251c\u2574')


_dominance_set_cache = {}  # type: Dict[FrozenSet[LR0Node], LR0DominanceSet]


def _find_common_parent(node_list):
    # type: (List[LR0Node]) -> List[LR0Node]
    node_set = frozenset(node_list)
    try:
        dominance_set = _dominance_set_cache[node_set]
    except KeyError:
        dominance_set = LR0DominanceSet(node_list)
        # dominance_set.print_dot()
        _dominance_set_cache[node_set] = dominance_set
    if dominance_set._best_dominator:
        return dominance_set._best_dominator._nodes
    return []


def _find_counterexamples(conflict_list):
    # type: (List[Tuple[LR0Node, Set[int]]]) -> List[Tuple[LR0Node, List[Tuple[LR0Node, LR0Path]]]]
    class IntermediateResult(object):

        def __init__(self, path_list):
            # type: (List[List[Tuple[LR0Node, LR0Path]]]) -> None
            self._paths = path_list
            self._refcount = 1

    conflict_paths = [
        (node, []) for node, _ in conflict_list
    ]  # type: List[Tuple[LR0Node, List[Tuple[LR0Node, LR0Path]]]]
    reduce_node = [1 if node._item == node._item._last else 0 for node, _ in conflict_list]

    lst = []  # type: List[List[Tuple[LR0Node, LR0Path, Set[int], Set[Union[Tuple[LR0Node, bool], LR0ItemSet]]]]]
    states = {
    }  # type: Dict[Tuple[LR0ItemSet, int], List[List[Tuple[LR0Node, LR0Path, Set[int], Set[Union[Tuple[LR0Node, bool], LR0ItemSet]]]]]]
    for s in conflict_list:
        lst.append([(s[0], LR0PathItem(s[0]._item), s[1], set())])
    intermediate_result = None  # type: Optional[IntermediateResult]
    queue = [(lst, intermediate_result, states)]

    while queue:
        path_list, intermediate_result, states = queue.pop(0)
        temp_result = []  # type: List[List[Tuple[LR0Node, LR0Path]]]
        recurse = False
        report = True
        all_nodes = []  # type: List[LR0Node]

        for paths in path_list:
            temp_result.append([])
            for node, path, lookahead, _ in paths:
                if node._item._index == 0 and not lookahead:
                    all_nodes.append(node)
                    temp_result[-1].append((node, path))
                else:
                    recurse = True
            if len(paths) > 0 and len(temp_result[-1]) == 0:
                report = False

        if report:
            common_parents = _find_common_parent(all_nodes)
            if common_parents:
                if recurse:
                    if intermediate_result is not None:
                        intermediate_result._refcount -= 1
                    intermediate_result = IntermediateResult([])
                    for index, tmp_paths in enumerate(temp_result):
                        intermediate_result._paths.append([])
                        for node, path in tmp_paths:
                            node, path = node.backtrack_to_any(path, common_parents)
                            intermediate_result._paths[index].append((node, path))
                else:
                    for index, tmp_paths in enumerate(temp_result):
                        for node, path in tmp_paths:
                            node, path = node.backtrack_to_any(path, common_parents)
                            conflict_paths[index][1].append((node, path))
            else:
                recurse = True

        if recurse:
            check_current_state = False
            if len(states) == 0:
                current_state = []
                for index, paths in enumerate(path_list):
                    current_state_paths = []
                    for node, path, lookahead, seen in paths:
                        predecessor_list = node.backtrack_up(path, lookahead, seen)
                        for predecessor, predecessor_path, la, consumed_token in predecessor_list:
                            if consumed_token is not None:
                                try:
                                    predecessors = states[(predecessor._item_set, consumed_token)]
                                except KeyError:
                                    predecessors = [[] for _ in path_list]
                                    states[(predecessor._item_set, consumed_token)] = predecessors
                                predecessors[index].append((predecessor, predecessor_path, la, seen))
                            else:
                                current_state_paths.append((predecessor, predecessor_path, la, set(seen)))
                    if current_state_paths:
                        check_current_state = True
                        current_state.append(current_state_paths)
                    else:
                        current_state.append(paths)

            if check_current_state:
                queue.insert(0, (current_state, intermediate_result, states))
            else:
                for (item_set, _), nodes_list in states.items():
                    count = 0
                    reduce_count = 0
                    for nodes, reduce in zip(nodes_list, reduce_node):
                        if len(nodes) > 0:
                            count += 1
                            reduce_count += reduce
                    if count > 1 and reduce_count > 0:
                        if intermediate_result is not None:
                            intermediate_result._refcount += 1
                        queue.append((nodes_list, intermediate_result, {}))
            if intermediate_result is not None:
                intermediate_result._refcount -= 1
                if intermediate_result._refcount == 0:
                    for index, tmp_paths in enumerate(intermediate_result._paths):
                        conflict_paths[index][1].extend(tmp_paths)

    return conflict_paths


def create_parser_table(
        productions, start_id, name_map, terminal_count, show_merges, sm_log, conflict_log, error_log,
        show_progress=False
):
    # type: (Dict[int, Grammar.Production], int, List[str], int, bool, Logger, Logger, Logger, bool) -> LALRTable
    cidhash = {}  # type: Dict[int, int]
    goto_cache = {}  # type: Dict[Tuple[int, int], Optional[LR0ItemSet]]
    goto_cache_2 = {}  # type: Dict[int, Any]

    def goto(item_set, index, lookahead):
        # type: (LR0ItemSet, int, int) -> Optional[LR0ItemSet]
        # First we look for a previously cached entry
        item_set_id = id(item_set)
        result = goto_cache.get((item_set_id, lookahead), None)
        if result is not None:
            return result

        s = goto_cache_2.get(lookahead)
        if not s:
            s = {}
            goto_cache_2[lookahead] = s

        gs = []  # type: List[Tuple[LR0Item, Optional[LR0Node], int]]
        for item in item_set:
            next = item._next
            if next and next._before == lookahead:
                gs.append((next, item_set[item], lookahead))

        gs = sorted(gs, key=lambda x: id(x[0]))
        for item, _, _ in gs:
            s1 = s.get(id(item))
            if not s1:
                s1 = {}
                s[id(item)] = s1
            s = s1

        result = s.get(0, None)
        if result is None:
            if gs:
                result = LR0ItemSet(index, gs)
                s[0] = result
            else:
                s[0] = None
        else:
            result.add_core(gs)

        goto_cache[(item_set_id, lookahead)] = result
        return result

    def create_item_sets():
        # type: () -> List[LR0ItemSet]
        assert len(productions[start_id]) == 1
        states = [LR0ItemSet(0, [(productions[start_id][0]._item, None, 2)])]
        cidhash[id(states[0])] = 0

        # Loop over the items in C and each grammar symbols
        i = 0
        while i < len(states):
            state = states[i]
            i += 1

            # Collect all of the symbols that could possibly be in the goto(I,X) sets
            asyms = set([])  # type: Set[int]
            for item in state:
                asyms.update(item._symbols)

            for x in sorted(asyms):
                g = goto(state, len(states), x)
                if not g or id(g) in cidhash:
                    continue
                cidhash[id(g)] = len(states)
                states.append(g)

        return states

    def add_lalr_lookahead(states):
        # type: (List[LR0ItemSet]) -> None

        def traverse(x, N, stack, F, X, R, FP):
            # type: (Tuple[int, int], Dict[Tuple[int, int], int], List[Tuple[int, int]], Dict[Tuple[int, int], List[int]], List[Tuple[int, int]], Callable[[Tuple[int, int]], List[Tuple[int, int]]], Callable[[Tuple[int, int]], List[int]]) -> None
            stack.append(x)
            d = len(stack)
            N[x] = d
            F[x] = FP(x)  # F(X) <- F'(x)

            rel = R(x)  # Get y's related to x
            for y in rel:
                if N[y] == 0:
                    traverse(y, N, stack, F, X, R, FP)
                N[x] = min(N[x], N[y])
                for a in F.get(y, []):
                    if a not in F[x]:
                        F[x].append(a)
            if N[x] == d:
                N[stack[-1]] = sys.maxsize
                F[stack[-1]] = F[x]
                element = stack.pop()
                while element != x:
                    N[stack[-1]] = sys.maxsize
                    F[stack[-1]] = F[x]
                    element = stack.pop()

        def digraph(X, R, FP):
            # type: (List[Tuple[int, int]], Callable[[Tuple[int, int]], List[Tuple[int, int]]], Callable[[Tuple[int, int]], List[int]]) -> Dict[Tuple[int, int], List[int]]
            N = {}
            for x in X:
                N[x] = 0
            stack = []  # type: List[Tuple[int, int]]
            F = {}  # type: Dict[Tuple[int, int], List[int]]
            for x in X:
                if N[x] == 0:
                    traverse(x, N, stack, F, X, R, FP)
            return F

        def dr_relation(trans):
            # type: (Tuple[int, int]) -> List[int]
            state, N = trans
            terms = []

            item_set = goto(states[state], len(states), N)
            assert item_set is not None
            for item in item_set:
                if item._index < item.len:
                    a = item.rule.production[item._index]
                    if a < terminal_count:
                        if a not in terms:
                            terms.append(a)

            # This extra bit is to handle the start state
            if state == start_id and N == productions[start_id][0].production[0]:
                terms.append(0)

            return terms

        def reads_relation(trans, empty):
            # type: (Tuple[int, int], Set[int]) -> List[Tuple[int, int]]
            # Look for empty transitions
            rel = []
            state, N = trans

            item_set = goto(states[state], len(states), N)
            assert item_set is not None
            j = cidhash[id(item_set)]
            for item in item_set:
                if item._index < item.len:
                    a = item.rule.production[item._index]
                    if a in empty:
                        rel.append((j, a))

            return rel

        def compute_read_sets(trans, nullable):
            # type: (List[Tuple[int, int]], Set[int]) -> Dict[Tuple[int, int], List[int]]
            FP = lambda x: dr_relation(x)
            R = lambda x: reads_relation(x, nullable)
            F = digraph(trans, R, FP)
            return F

        def compute_lookback_includes(trans, nullable):
            # type: (List[Tuple[int, int]], Set[int]) -> Tuple[Dict[Tuple[int, int], List[Tuple[int, LR0Item]]], Dict[Tuple[int, int], List[Tuple[int, int]]]]
            lookdict = {}  # Dictionary of lookback relations
            includedict = {}  # type: Dict[Tuple[int, int], List[Tuple[int, int]]]

            # Make a dictionary of non-terminal transitions
            dtrans = {}
            for t1 in trans:
                dtrans[t1] = 1

            # Loop over all transitions and compute lookbacks and includes
            for state, N in trans:
                lookb = []
                includes = []
                for p in states[state]:
                    if p.rule._prod_symbol != N:
                        continue

                    # Okay, we have a name match.  We now follow the production all the way
                    # through the state machine until we get the . on the right hand side

                    lr_index = p._index
                    j = state
                    while lr_index < p.len:
                        t = p.rule.production[lr_index]
                        lr_index = lr_index + 1

                        # Check to see if this symbol and state are a non-terminal transition
                        if (j, t) in dtrans:
                            # Yes.  Okay, there is some chance that this is an includes relation
                            # the only way to know for certain is whether the rest of the
                            # production derives empty

                            li = lr_index
                            while li < p.len:
                                if p.rule.production[li] < terminal_count:
                                    break  # No forget it
                                if p.rule.production[li] not in nullable:
                                    break
                                li = li + 1
                            else:
                                # Appears to be a relation between (j,t) and (state,N)
                                includes.append((j, t))

                        g = goto(states[j], len(states), t)  # Go to next set
                        j = cidhash[id(g)]  # Go to next state

                    # When we get here, j is the final state, now we have to locate the production
                    for r in states[j]:
                        if r.rule._prod_symbol != p.rule._prod_symbol:
                            continue
                        if r.len != p.len:
                            continue
                        # i = 0
                        # This look is comparing a production ". A B C" with "A B C ."
                        # while i < r._index:
                        #    if r._rule[i] != p._rule[i + 1]:
                        #        break
                        #    i = i + 1
                        # else:
                        #    lookb.append((j, r))
                        if p._index == 0 and r.rule.production[:r._index] == p.rule.production[:r._index]:
                            lookb.append((j, r))
                for ii in includes:
                    if ii not in includedict:
                        includedict[ii] = []
                    includedict[ii].append((state, N))
                lookdict[(state, N)] = lookb

            return lookdict, includedict

        def compute_follow_sets(ntrans, readsets, inclsets):
            # type: (List[Tuple[int, int]], Dict[Tuple[int, int], List[int]], Dict[Tuple[int, int], List[Tuple[int, int]]]) -> Dict[Tuple[int, int], List[int]]
            FP = lambda x: readsets[x]
            R = lambda x: inclsets.get(x, [])
            F = digraph(ntrans, R, FP)
            return F

        def add_lookaheads(lookbacks, followset):
            # type: (Dict[Tuple[int, int], List[Tuple[int, LR0Item]]], Dict[Tuple[int, int], List[int]]) -> None
            for trans, lb in lookbacks.items():
                # Loop over productions in lookback
                for state, p in lb:
                    if state not in p._lookaheads:
                        p._lookaheads[state] = []
                    l = p._lookaheads[state]
                    f = followset.get(trans, [])
                    for a in f:
                        if a not in l:
                            l.append(a)

        # Determine all of the nullable nonterminals
        nullable = set([])
        for prod_symbol, prod in productions.items():
            if prod._empty:
                nullable.add(prod_symbol)

        # Find all non-terminal transitions
        trans = []
        for stateno, state in enumerate(states):
            for item in state:
                if item._index < item.len:
                    t = (stateno, item.rule.production[item._index])
                    if t[1] >= terminal_count:
                        if t not in trans:
                            trans.append(t)

        # Compute read sets
        readsets = compute_read_sets(trans, nullable)

        # Compute lookback/includes relations
        lookd, included = compute_lookback_includes(trans, nullable)

        # Compute LALR FOLLOW sets
        followsets = compute_follow_sets(trans, readsets, included)

        # Add all of the lookaheads
        add_lookaheads(lookd, followsets)

    goto_table = []  # Goto array
    action = []  # Action array

    # Build the parser table, state by state
    states = create_item_sets()
    add_lalr_lookahead(states)

    st = 0

    priority_missing = {}  # type: Dict[LR0Item, List[int]]
    split_missing = {}  # type: Dict[LR0Item, List[int]]
    merge_missing = {}  # type: Dict[LR0Item, List[int]]

    priority_conflict = {}  # type: Dict[FrozenSet[LR0Item], List[int]]
    conflict_issues = {}  # type: Dict[FrozenSet[LR0Item], Dict[LR0Item, List[Tuple[LR0Node, LR0Path]]]]
    merge_requests = {}  # type: Dict[int, List[Tuple[Set[str], Dict[str, Set[LR0Path]]]]]

    num_rr = 0
    num_sr = 0

    bar_size = get_terminal_size()[1] - 2
    for st, item_group in enumerate(states):
        # Loop over each production
        completed = int(bar_size * (1 + st) / len(states))
        remaining = bar_size - completed
        if show_progress:
            if sys.version_info >= (3,):
                sys.stdout.write('\r[\x1b[32m%s\x1b[37m%s\x1b[0m]' % ('\u2501' * completed, '\u2501' * remaining))
            else:
                sys.stdout.write(
                    (u'\r[\x1b[32m%s\x1b[37m%s\x1b[0m]' %
                     (u'\u2501' * completed, u'\u2501' * remaining)).encode('utf-8')
                )
        action_map = {}  # type: Dict[int, List[Tuple[int, LR0Item]]]
        st_action = {}  # type: Dict[int, Tuple[Tuple[int, Optional[str]],...]]
        st_goto = {}  # type: Dict[int, int]
        merges = {}  # type: Dict[FrozenSet[LR0Item], Tuple[Set[int], Set[LR0Node]]]

        sm_log.info('')
        sm_log.info('')
        sm_log.info('state %d:', st)
        sm_log.info('')
        for item in item_group:
            sm_log.info('    (%d) %s', item.rule._id, item.to_string(name_map))
        sm_log.info('')

        for item in item_group:
            if item._last == item:
                if item.rule._prod_symbol == start_id:
                    # Start symbol. Accept!
                    action_map[-1] = [(-item.rule._id, item)]
                    item.rule._reduced += 1
                else:
                    # We are at the end of a production.  Reduce!
                    for a in item._lookaheads[st]:
                        action_map[a] = action_map.get(a, []) + [(-item.rule._id, item)]
                        item.rule._reduced += 1
            else:
                i = item._index
                a = item.rule.production[i]  # Get symbol right after the "."
                if a < terminal_count:
                    g = goto(item_group, len(states), a)
                    j = cidhash[id(g)]
                    if j >= 0:
                        action_map[a] = action_map.get(a, []) + [(j, item)]

        for a in sorted(action_map):
            actions = action_map[a]
            action_dest = {}  # type: Dict[int, List[LR0Item]]
            for i, item in actions:
                try:
                    action_dest[i].append(item)
                except KeyError:
                    action_dest[i] = [item]

            accepted_actions = {}  # type: Dict[int, List[LR0Item]]

            if len(action_dest) > 1:
                # looks like a potential conflict, look at precedence
                conflict_log.info('State %d:', st)
                conflict_log.info('  disambiguation for lookahead %s', name_map[a])

                precedence, associativity = (-1, 'nonassoc')
                shift_actions = False
                reduce_actions = False
                assoc_error = False
                precedence_set = False
                split = True
                all_items = []
                for j, items in action_dest.items():
                    all_items += items
                    for item in items:
                        if item._precedence is not None:
                            if item._precedence[1] > precedence:
                                precedence_set = True
                                precedence = item._precedence[1]
                                associativity = item._precedence[0]
                                assoc_error = False
                                shift_actions = j >= 0
                                reduce_actions = j < 0
                                split = item._split is not None
                            elif item._precedence[1] == precedence:
                                if precedence_set:
                                    if item._precedence[0] != associativity:
                                        assoc_error = True
                                    shift_actions |= j >= 0
                                    reduce_actions |= j < 0
                                    split &= item._split is not None
                                else:
                                    associativity = item._precedence[0]
                                    precedence_set = True
                                    assoc_error = False
                                    shift_actions = j >= 0
                                    reduce_actions = j < 0
                                    split = item._split is not None
                        elif precedence == -1:
                            shift_actions |= j >= 0
                            reduce_actions |= j < 0
                            split &= item._split is not None

                all_items_set = frozenset(all_items)

                if assoc_error:
                    try:
                        priority_conflict[all_items_set].append(st)
                    except KeyError:
                        priority_conflict[all_items_set] = [st]

                for j, items in action_dest.items():
                    for item in items:
                        if item._precedence is None and precedence_set:
                            if j >= 0:
                                try:
                                    priority_missing[item].append(st)
                                except KeyError:
                                    priority_missing[item] = [st]
                                conflict_log.info('  [no precedence] %s', item.to_string(name_map))
                            else:
                                conflict_log.info('  [discarded] %s', item.to_string(name_map))
                                try:
                                    item_group._discarded[item].add(a)
                                except KeyError:
                                    item_group._discarded[item] = set([a])
                            continue
                        elif item._precedence is not None:
                            if item._precedence[1] < precedence:
                                conflict_log.info('  [discarded] %s', item.to_string(name_map))
                                try:
                                    item_group._discarded[item].add(a)
                                except KeyError:
                                    item_group._discarded[item] = set([a])
                                continue
                            if j < 0 and shift_actions and associativity == 'left':
                                conflict_log.info('  [discarded] %s', item.to_string(name_map))
                                try:
                                    item_group._discarded[item].add(a)
                                except KeyError:
                                    item_group._discarded[item] = set([a])
                                continue
                            if j >= 0 and reduce_actions and associativity == 'right':
                                conflict_log.info('  [discarded] %s', item.to_string(name_map))
                                try:
                                    item_group._discarded[item].add(a)
                                except KeyError:
                                    item_group._discarded[item] = set([a])
                                continue
                        if split and item._split is None:
                            try:
                                split_missing[item].append(st)
                            except KeyError:
                                split_missing[item] = [st]
                        try:
                            accepted_actions[j].append(item)
                        except KeyError:
                            accepted_actions[j] = [item]
                        conflict_log.info('  [accepted]  %s', item.to_string(name_map))
                conflict_log.info('')
            else:
                accepted_actions = action_dest

            st_action[a] = tuple(sorted([(j, items[0]._split) for j, items in accepted_actions.items()]))
            if len(accepted_actions) > 1 and not split:
                # handle conflicts
                conflicts = []  # type: List[Tuple[LR0Node, Set[int]]]
                num_rr += 1
                sm_log.info('    %-30s conflict split', name_map[a])
                for j, _ in st_action[a]:
                    items = accepted_actions[j]
                    if j >= 0:
                        sm_log.info('        shift and go to state %d', j)
                        num_rr -= 1
                        num_sr += 1
                    for item in items:
                        node = item_group[item]
                        if j >= 0:
                            conflicts.append((node, set()))
                        else:
                            sm_log.info('        reduce using rule %s', item.to_string(name_map))
                            conflicts.append((node, set([a])))

                counterexamples = _find_counterexamples(conflicts)
                result_count = 0
                for node, conflict_list in counterexamples:
                    if conflict_list:
                        result_count += 1
                if result_count == 0:
                    conflict_log.info('  unable to find counterexamples - lookahead: %s\n' % name_map[a])
                    error_log.warning('unable to find counterexamples - lookahead: %s' % name_map[a])

                conflict_items = frozenset(node._item for node, _ in counterexamples)
                try:
                    item_conflict_node = conflict_issues[conflict_items]
                except KeyError:
                    item_conflict_node = {}
                    conflict_issues[conflict_items] = item_conflict_node
                for node, paths in counterexamples:
                    try:
                        item_conflict_node[node._item] += paths
                    except KeyError:
                        item_conflict_node[node._item] = paths
            elif len(accepted_actions) > 1:
                sm_log.info('    %-30s split', name_map[a])
                split_error = False
                split_names = set()
                key = frozenset((item for (j, _) in st_action[a] for item in accepted_actions[j]))
                try:
                    merge_lookaheads, merge_nodes = merges[key]
                    merge_lookaheads.add(a)
                except KeyError:
                    merge_lookaheads = set([a])
                    merge_nodes = set()
                    merges[key] = (merge_lookaheads, merge_nodes)

                sm_log.info('    %-30s split', name_map[a])
                for action_index, (j, split_name) in enumerate(st_action[a]):
                    if split_name in split_names:
                        split_error = True
                    split_names.add(split_name)
                    items = accepted_actions[j]
                    if j >= 0:
                        sm_log.info('        shift and go to state %d', j)
                        for item in items:
                            if item._split != split_name:
                                split_error = True

                    for item in items:
                        item._split_use += 1
                        assert item._split is not None
                        merge_nodes.add(item_group[item])
                        if j < 0:
                            sm_log.info('        reduce using rule %s', item.to_string(name_map))
                if split_error:
                    error_log.error('split tag mismatch in state %d for token \'%s\':' % (st, name_map[a]))
                    error_log.note('  ensure all reduce rules have different names')
                    error_log.note('  ensure all shift rules have the same name')
                    for j, split_name in st_action[a]:
                        for item in accepted_actions[j]:
                            error_log.note('    %s' % item.to_string(name_map))

                if show_merges:
                    splits = [
                        (node, node._item._next is None, node._item._split or ('_%d' % merge_index))
                        for merge_index, node in enumerate(merge_nodes)
                    ]
                    conflict_log.info('   Merge graph for rules:')
                    for node, _, split_name in splits:
                        conflict_log.info(
                            '      [%s][%s] %s' % (split_name, name_map[a], node._item.to_string(name_map))
                        )
                    _find_merge_points(splits, a, name_map, conflict_log, error_log)
                    conflict_log.info('')
            else:
                for j, _ in st_action[a]:
                    items = accepted_actions[j]
                    if j >= 0:
                        sm_log.info('    %-30s[%d] shift and go to state %d', name_map[a], a, j)
                    for item in items:
                        if j < 0:
                            sm_log.info('    %-30s reduce using rule %s', name_map[a], item.to_string(name_map))

        # for lookaheads, nodes in merges.values():
        #    local_paths = {}                                                                     # type: Dict[int, Dict[str, Set[LR0Path]]]
        #    for la in lookaheads:
        #        counterexamples = _find_counterexamples(
        #            [(node, set([la]) if node._item._next is None else set()) for node in nodes]
        #        )
        #        for source_node, paths in counterexamples:
        #            assert source_node._item._split is not None
        #            split_name = source_node._item._split
        #            for target_node, path in paths:
        #                symbol = target_node._item._symbol
        #                try:
        #                    param_paths = local_paths[symbol]
        #                except KeyError:
        #                    local_paths[symbol] = {split_name: set([path])}
        #                else:
        #                    try:
        #                        param_paths[split_name].add(path)
        #                    except KeyError:
        #                        param_paths[split_name] = set([path])
        #    for symbol, param_paths in local_paths.items():
        #        try:
        #            merge_requests[symbol].append((set(param_paths.keys()), param_paths))
        #        except KeyError:
        #            merge_requests[symbol] = [(set(param_paths.keys()), param_paths)]

        nkeys = set([])
        for item in item_group:
            for s in item._symbols:
                if s >= terminal_count:
                    g = goto(item_group, len(states), s)
                    j = cidhash.get(id(g), -1)
                    if j >= 0:
                        if s not in nkeys:
                            st_goto[s] = j
                            nkeys.add(s)
                            sm_log.info('    %-30s shift and go to state %d', name_map[s], j)
                            # assert item._next is not None

        action.append(st_action)
        goto_table.append(st_goto)

    # process merges
    for symbol, merge_list in merge_requests.items():
        while merge_list:
            params, param_paths = merge_list.pop(-1)
            for m in merge_list:
                if not m[0].isdisjoint(params):
                    m[0].update(params)
                    for param, path_set in param_paths.items():
                        try:
                            m[1][param].update(path_set)
                        except KeyError:
                            m[1][param] = path_set
                    break
            else:
                conflict_log.info('def %s_merge(%s):' % (name_map[symbol], ', '.join(sorted(params))))
                for param, path_set in sorted(param_paths.items()):
                    conflict_log.info('    # %s' % param)
                    for path in path_set:
                        for string in path.to_string(name_map):
                            conflict_log.info('    # # %s' % string)
                        conflict_log.info('    #')
                    conflict_log.info('    #')

    # Report errors
    sys.stdout.write('\n')
    for _, production in productions.items():
        for rule in production:
            if rule._reduced == 0:
                error_log.warning('Rule (%s) is never reduced', rule.to_string(name_map))

    for missing, text in (
            (priority_missing, 'precedence'),
            (split_missing, 'split'),
            (merge_missing, 'merge'),
    ):
        if len(missing) == 1:
            error_log.warning('1 missing %s annotation', text)
        elif len(missing) > 1:
            error_log.warning('%d missing %s annotations', len(missing), text)
        for item, _ in sorted(missing.items(), key=lambda x: (x[0].rule._filename, x[0].rule._lineno)):
            error_log.diagnostic(item.rule._filename, item.rule._lineno, item.to_string(name_map))

    if len(priority_conflict) == 1:
        error_log.warning('1 conflicting precedence annotation')
    elif len(priority_conflict) > 1:
        error_log.warning('%d conflicting precedence annotations', len(priority_conflict))
    for item_set, state_numbers in priority_conflict.items():
        error_log.warning('conflicting precedence in states %s:', ', '.join([str(i) for i in state_numbers]))
        for item in sorted(item_set, key=lambda x: (x.rule._filename, x.rule._lineno)):
            error_log.diagnostic(item.rule._filename, item.rule._lineno, item.to_string(name_map))

    if show_merges:
        for _, production in sorted(productions.items()):
            for rule in production:
                item_iterator = rule._item  # type: Optional[LR0Item]
                while item_iterator:
                    if item_iterator._split is not None and item_iterator._split_use == 0:
                        error_log.warning('unused split annotation')
                        error_log.diagnostic(rule._filename, rule._lineno, item_iterator.to_string(name_map))
                    item_iterator = item_iterator._next

            for merge in rule._item._last._merges:
                if merge._use_count == 0:
                    error_log.warning('unused merge annotation %s' % merge._action._method_name)
                    error_log.diagnostic(
                        merge._action._filename, merge._action._lineno,
                        '%s(%s)' % (merge._action._method_name, ', '.join(merge._arguments))
                    )
                else:
                    for argument, use_count in merge._arguments.items():
                        if use_count == 0:
                            error_log.warning('unused merge arguments "%s"' % argument)
                            error_log.diagnostic(
                                merge._action._filename, merge._action._lineno,
                                '%s(%s)' % (merge._action._method_name, ', '.join(merge._arguments))
                            )

    if num_sr == 1:
        error_log.warning('1 shift/reduce conflict')
    elif num_sr > 1:
        error_log.warning('%d shift/reduce conflicts', num_sr)

    if num_rr == 1:
        error_log.warning('1 reduce/reduce conflict')
    elif num_rr > 1:
        error_log.warning('%d reduce/reduce conflicts', num_rr)

    for item_set, conflict_set in conflict_issues.items():
        conflict_log.info('conflict:')
        for item in sorted(item_set, key=lambda x: (x.rule._filename, x.rule._lineno)):
            conflict_log.info('  %s', item.to_string(name_map))
        conflict_log.info('')
        for (item, paths) in sorted(conflict_set.items(), key=lambda x: (x[0].rule._filename, x[0].rule._lineno)):
            _log(
                '%s using rule %s' % ('reduce' if item == item._last else 'shift', item.to_string(name_map)),
                sorted(
                    [p for _, p in paths],
                    key=lambda p: (
                        p._items[0][1].rule._prod_name,
                        p._items[0][1].rule._filename,
                        p._items[0][1].rule._lineno,
                    )
                ), conflict_log, name_map
            )

    return LALRTable(action, goto_table)


if TYPE_CHECKING:
    from typing import Any, Callable, Dict, FrozenSet, List, Optional, Set, Text, Tuple, Union
    from .grammar import Grammar
    from .lr0item import LR0Item
    from .lr0path import LR0Path
    from ..log import Logger
