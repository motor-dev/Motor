from .lr0itemset import LR0ItemSet
from .lr0dominancenode import LR0DominanceNode
from .lr0path import LR0Path
from be_typing import TYPE_CHECKING
import sys


def _log(title, conflict_paths, out, name_map):
    # type: (str, List[LR0Path], Logger, List[str]) -> None
    seen = set([])
    if conflict_paths:
        count = len(set(conflict_paths))
        out.info('   %s' % (title))
        out.info('   \u256d\u2574')
        for path in conflict_paths:
            if path in seen:
                continue
            count -= 1
            seen.add(path)
            strings = path.expand_left().to_string(name_map)[0]
            for s in strings:
                out.info('   \u2502 %s' % s)
            if count == 0:
                out.info('   \u2570\u2574')
            else:
                out.info('   \u251c\u2574')


def _log_counterexamples(conflict_list, out, first_set, name_map):
    # type: (List[Tuple[LR0DominanceNode, str, Optional[int]]], Logger, Dict[int, Set[int]], List[str]) -> List[LR0Item]
    conflict_paths = [(message, []) for _, message, _ in conflict_list] # type: List[Tuple[str, List[LR0Path]]]
    result = []                                                         # type: List[LR0Item]

    queue = []     # type: List[List[Tuple[LR0Path, Optional[int], Set[Tuple[LR0DominanceNode, Optional[int]]], int]]]

    queue.append(
        [(LR0Path(node, []), lookahead, set(), index) for index, (node, _, lookahead) in enumerate(conflict_list)]
    )
    while queue:
        path_list = queue.pop(0)
        #assert path_1._node.item_set == path_2._node.item_set
        path_len = 0
        found_lookaheads = True
        for path, lookahead, _, _ in path_list:
            path_len = max(path_len, path._node._item._index)
            found_lookaheads &= lookahead is None

        if path_len == 0:
            if found_lookaheads:
                for path, _, _, index in path_list:
                    conflict_paths[index][1].append(path)
            else:
                states = {
                }              # type: Dict[LR0ItemSet, List[Tuple[LR0Path, Optional[int], Set[Tuple[LR0DominanceNode, Optional[int]]], int]]]

                for path, lookahead, seen, index in path_list:
                    if lookahead is not None:
                        for path, la in path._node.backtrack_up(path, None, lookahead, first_set, seen):
                            try:
                                states[path._node._item_set].append((path, la, seen, index))
                            except KeyError:
                                states[path._node._item_set] = [(path, la, seen, index)]
                for state, plist in states.items():
                    for path, lookahead, seen, index in path_list:
                        if lookahead is None:
                            if path._node._item_set == state:
                                plist.append((path, lookahead, seen, index))
                            else:
                                for path, la in path._node.backtrack_up(path, state, lookahead, first_set, seen):
                                    #assert path1._node.item_set == path2._node.item_set
                                    plist.append((path, la, seen, index))
                for _, plist in states.items():
                    queue.append(plist)
        else:
            states = {}
            for path, lookahead, seen, index in path_list:
                if path._node._item._index > 0:
                    for path, la in path._node.backtrack_up(path, None, lookahead, first_set, seen):
                        try:
                            states[path._node._item_set].append((path, la, seen, index))
                        except KeyError:
                            states[path._node._item_set] = [(path, la, seen, index)]
            for state, plist in states.items():
                for path, lookahead, seen, index in path_list:
                    if path._node._item._index == 0:
                        for path, la in path._node.backtrack_up(path, state, lookahead, first_set, seen):
                            #assert path1._node.item_set == path2._node.item_set
                            plist.append((path, la, seen, index))
            for _, plist in states.items():
                queue.append(plist)

    for message, conflicts in conflict_paths:
        _log(message, conflicts, out, name_map)
        out.info('')
    return result


def create_parser_table(productions, start_id, name_map, terminal_count, log, error_log, dot_file):
    # type: (Dict[int, Grammar.Production], int, List[str], int, Logger, Logger, Logger) -> None
    cidhash = {}
    goto_cache = {}    # type: Dict[Tuple[int, int], Optional[LR0ItemSet]]
    goto_cache_2 = {}  # type: Dict[int, Any]
    first_set = {}
    for prod_index, prod in productions.items():
        first_set[prod_index] = prod._first

    def goto(item_set, lookahead):
        # type: (LR0ItemSet, int) -> Optional[LR0ItemSet]
        # First we look for a previously cached entry
        item_set_id = id(item_set)
        result = goto_cache.get((item_set_id, lookahead), None)
        if result is not None:
            return result

        s = goto_cache_2.get(lookahead)
        if not s:
            s = {}
            goto_cache_2[lookahead] = s

        gs = []    # type: List[Tuple[LR0Item, Optional[LR0DominanceNode], int]]
        for item in item_set:
            next = item._next
            if next and next._before == lookahead:
                s1 = s.get(id(next))
                if not s1:
                    s1 = {}
                    s[id(next)] = s1
                gs.append((next, item_set._items[item], lookahead))
                s = s1

        result = s.get(0, None)
        if result is None:
            if gs:
                result = LR0ItemSet(gs)
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
        states = [LR0ItemSet([(productions[start_id][0]._item, None, 2)])]
        cidhash[id(states[0])] = 0

        # Loop over the items in C and each grammar symbols
        i = 0
        while i < len(states):
            state = states[i]
            i += 1

            # Collect all of the symbols that could possibly be in the goto(I,X) sets
            asyms = set([])
            for item in state:
                for s in item._symbols:
                    asyms.add(s)

            for x in asyms:
                g = goto(state, x)
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
            F[x] = FP(x)   # F(X) <- F'(x)

            rel = R(x)     # Get y's related to x
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
            stack = []     # type: List[Tuple[int, int]]
            F = {}         # type: Dict[Tuple[int, int], List[int]]
            for x in X:
                if N[x] == 0:
                    traverse(x, N, stack, F, X, R, FP)
            return F

        def dr_relation(trans):
            # type: (Tuple[int, int]) -> List[int]
            state, N = trans
            terms = []

            item_set = goto(states[state], N)
            assert item_set is not None
            for item in item_set:
                if item._index < len(item._rule):
                    a = item._rule._production[item._index]
                    if a < terminal_count:
                        if a not in terms:
                            terms.append(a)

            # This extra bit is to handle the start state
            if state == start_id and N == productions[start_id][0][0]:
                terms.append(0)

            return terms

        def reads_relation(trans, empty):
            # type: (Tuple[int, int], Set[int]) -> List[Tuple[int, int]]
            # Look for empty transitions
            rel = []
            state, N = trans

            item_set = goto(states[state], N)
            assert item_set is not None
            j = cidhash[id(item_set)]
            for item in item_set:
                if item._index < len(item._rule):
                    a = item._rule[item._index]
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
            lookdict = {}      # Dictionary of lookback relations
            includedict = {}   # type: Dict[Tuple[int, int], List[Tuple[int, int]]]

            # Make a dictionary of non-terminal transitions
            dtrans = {}
            for t1 in trans:
                dtrans[t1] = 1

            # Loop over all transitions and compute lookbacks and includes
            for state, N in trans:
                lookb = []
                includes = []
                for p in states[state]:
                    if p._rule._prod_symbol != N:
                        continue

                    # Okay, we have a name match.  We now follow the production all the way
                    # through the state machine until we get the . on the right hand side

                    lr_index = p._index
                    j = state
                    while lr_index < len(p._rule):
                        t = p._rule[lr_index]
                        lr_index = lr_index + 1

                        # Check to see if this symbol and state are a non-terminal transition
                        if (j, t) in dtrans:
                            # Yes.  Okay, there is some chance that this is an includes relation
                            # the only way to know for certain is whether the rest of the
                            # production derives empty

                            li = lr_index
                            while li < len(p._rule):
                                if p._rule[li] < terminal_count:
                                    break # No forget it
                                if p._rule[li] not in nullable:
                                    break
                                li = li + 1
                            else:
                                          # Appears to be a relation between (j,t) and (state,N)
                                includes.append((j, t))

                        g = goto(states[j], t) # Go to next set
                        j = cidhash[id(g)]     # Go to next state

                    # When we get here, j is the final state, now we have to locate the production
                    for r in states[j]:
                        if r._rule._prod_symbol != p._rule._prod_symbol:
                            continue
                        if len(r._rule) != len(p._rule):
                            continue
                        # i = 0
                        # This look is comparing a production ". A B C" with "A B C ."
                        # while i < r._index:
                        #    if r._rule[i] != p._rule[i + 1]:
                        #        break
                        #    i = i + 1
                        #else:
                        #    lookb.append((j, r))
                        if p._index == 0 and r._rule._production[:r._index] == p._rule._production[:r._index]:
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
                if item._index < len(item._rule):
                    t = (stateno, item._rule[item._index])
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

    goto_table = {}    # Goto array
    action = {}        # Action array
    actionp = {}       # Action production array (temporary)

    # Build the parser table, state by state
    states = create_item_sets()
    add_lalr_lookahead(states)

    st = 0

    num_missing_annotations = 0
    num_rr = 0

    dot_file.info('digraph Grammar {')
    for item_group in states:
        dot_file.info("  subgraph cluster_%d {", st)
        dot_file.info('    label="State %d";', st)
        dot_file.info('    style=filled;')
        dot_file.info('    color=lightgray;')
        dot_file.info('    node[style=filled;color=white];')
        state_id = id(item_group)
        for item in item_group:
            dot_file.info('    %d[label="%s"];', id(item_group._items[item]), item.to_string(name_map))
        for item in item_group:
            dnode = item_group._items[item]
            for child in dnode._direct_children:
                dot_file.info('    %d -> %d;', id(child), id(dnode))
        dot_file.info("  }")
        st += 1

    for st, item_group in enumerate(states):
        for _, node in item_group._items.items():
            for predecessor in node._predecessors:
                assert node._predecessor_lookahead is not None
                dot_file.info(
                    '  %d -> %d[label="%s"];', id(predecessor), id(node), name_map[node._predecessor_lookahead]
                )

        # Loop over each production
        st_action = {}     # type: Dict[int, List[Tuple[int, LR0Item]]]
        st_goto = {}
        log.info('state %d:', st)
        log.info('')
        for item in item_group:
            log.info('    (%d) %s', item._rule._prod_symbol, item.to_string(name_map))
        log.info('')

        for item in item_group:
            if len(item._rule) == item._index:
                if item._rule._prod_symbol == start_id:
                    # Start symbol. Accept!
                    st_action[0] = st_action.get(0, []) + [(0, item)]
                    item._rule._reduced += 1
                else:
                    # We are at the end of a production.  Reduce!
                    for a in item._lookaheads[st]:
                        st_action[a] = st_action.get(a, []) + [(-item._rule._id, item)]
                        item._rule._reduced += 1
            else:
                i = item._index
                a = item._rule[i]  # Get symbol right after the "."
                if a < terminal_count:
                    g = goto(item_group, a)
                    j = cidhash[id(g)]
                    if j >= 0:
                        st_action[a] = st_action.get(a, []) + [(j, item)]

        for a, actions in st_action.items():
            action_dest = {}   # type: Dict[int, List[LR0Item]]
            for i, item in actions:
                try:
                    action_dest[i].append(item)
                except KeyError:
                    action_dest[i] = [item]

            accepted_actions = {}  # type: Dict[int, List[LR0Item]]

            if len(action_dest) > 1:
                # looks like a potential conflict, look at precedence
                actions = sorted(actions, key=lambda x: x[1]._precedence[1] if x[1]._precedence is not None else -1)
                precedence = actions[-1][1]._precedence[1] if actions[-1][1]._precedence is not None else -1
                associativity = actions[-1][1]._precedence[0] if actions[-1][1]._precedence is not None else 'left'
                for _, item in actions:
                    if item._precedence is None:
                        log.info('  ** %s has no precedence annotation', item.to_string(name_map))
                        num_missing_annotations += 1
                assoc_conflict = False
                for j, item in actions:
                    if item._precedence is not None:
                        if item._precedence[1] < precedence:
                            log.info('  -- %s is not used', item.to_string(name_map))
                        elif item._precedence[0] != associativity:
                            log.error('  *** associativity conflicts!')
                            log.error('  *** %s', item.to_string(name_map))
                            assoc_conflict = True
                        elif associativity == 'left' and j >= 0:
                            try:
                                accepted_actions[j].append(item)
                            except KeyError:
                                accepted_actions[j] = [item]
                        elif associativity == 'right' and j < 0:
                            try:
                                accepted_actions[j].append(item)
                            except KeyError:
                                accepted_actions[j] = [item]
                        elif associativity == 'nonassoc':
                            try:
                                accepted_actions[j].append(item)
                            except KeyError:
                                accepted_actions[j] = [item]
                        else:
                            log.info('  -- %s is not used', item.to_string(name_map))
                    else:
                        try:
                            accepted_actions[j].append(item)
                        except KeyError:
                            accepted_actions[j] = [item]

                if assoc_conflict:
                    log.error('  *** %s', actions[-1][1].to_string(name_map))
                    log.error('  *** using %s', actions[-1][1].to_string(name_map))
            else:
                accepted_actions = action_dest

            if len(accepted_actions) > 1:
                # handle conflicts
                conflicts = []     # type: List[Tuple[LR0DominanceNode, str, Optional[int]]]
                for j, items in accepted_actions.items():
                    for item in items:
                        node = item_group[item]
                        if j > 0:
                            conflicts.append((node, 'Shift using rule %s' % item.to_string(name_map), None))
                        else:
                            conflicts.append((node, 'Reduce using rule %s' % item.to_string(name_map), a))
                _log_counterexamples(conflicts, log, first_set, name_map)

        nkeys = set([])
        for item in item_group:
            for s in item._symbols:
                if s > terminal_count:
                    g = goto(item_group, s)
                    j = cidhash.get(id(g), -1)
                    if j >= 0:
                        if s not in nkeys:
                            nkeys.add(s)
                            log.info('    %-30s shift and go to state %d', name_map[s], j)
        """
        # Print the actions associated with each terminal
        _actprint = {}
        for a, p, m in actlist:
            if a in st_action:
                if p is st_actionp[a]:
                    log.info('    %-15s %s', name_map[a], m)
                    _actprint[(a, m)] = 1
        log.info('')
        # Print the actions that were not used. (debugging)
        not_used = 0
        for a, p, m in actlist:
            if a in st_action:
                if p is not st_actionp[a]:
                    if not (a, m) in _actprint:
                        log.note('  ! %-15s [ %s ]', name_map[a], m)
                        not_used = 1
                        _actprint[(a, m)] = 1
        if not_used:
            log.note('')

        # Construct the goto table for this state

        nkeys = set([])    # type: Set[int]
        for item in item_group:
            for s in item._symbols:
                if s > terminal_count:
                    nkeys.add(s)
        for n in nkeys:
            g = goto(item_group, n)
            j = cidhash.get(id(g), -1)
            if j >= 0:
                st_goto[n] = j
                log.info('    %-30s shift and go to state %d', name_map[n], j)

        action[st] = st_action
        goto_table[st] = st_goto
        st += 1

        for state, tok, rule, resolution in sr_conflicts:
            log.warning('shift/reduce conflict for %s in state %d resolved as %s', name_map[tok], state, resolution)
            log.warning('  reduce rule %s', rule.to_string(name_map))
            error_log.warning(
                'shift/reduce conflict for %s in state %d resolved as %s', name_map[tok], state, resolution
            )
            error_log.warning('  reduce rule %s', rule.to_string(name_map))

        already_reported = set()
        for state, rule, rejected in rr_conflicts:
            if (state, id(rule), id(rejected)) in already_reported:
                continue
            log.warning('reduce/reduce conflict in state %d resolved using rule (%s)', state, rule.to_string(name_map))
            log.warning('rejected rule (%s) in state %d', rejected.to_string(name_map), state)
            error_log.warning(
                'reduce/reduce conflict in state %d resolved using rule (%s)', state, rule.to_string(name_map)
            )
            error_log.warning('rejected rule (%s) in state %d', rejected.to_string(name_map), state)
            already_reported.add((state, id(rule), id(rejected)))
        """
    dot_file.info('}')

    # Report shift/reduce and reduce/reduce conflicts
    if num_missing_annotations == 1:
        log.warning('1 missing precedence annotation')
        error_log.warning('1 missing precedence annotation')
    elif num_missing_annotations > 1:
        log.warning('%d missing precedence annotations', num_missing_annotations)
        error_log.warning('%d missing precedence annotations', num_missing_annotations)

    if num_rr == 1:
        log.warning('1 reduce/reduce conflict')
    elif num_rr > 1:
        log.warning('%d reduce/reduce conflicts', num_rr)
        error_log.warning('%d reduce/reduce conflicts', num_rr)

    for _, production in productions.items():
        for rule in production:
            if rule._reduced == 0:
                log.warning('Rule (%s) is never reduced', rule.to_string(name_map))


if TYPE_CHECKING:
    from be_typing import Any, Callable, Dict, List, Optional, Set, Tuple
    from .grammar import Grammar
    from .lr0item import LR0Item
    from .lr0path import LR0Path
    from ..log import Logger