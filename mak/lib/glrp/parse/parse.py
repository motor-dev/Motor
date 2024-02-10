from .production import Production
from .grammar import Grammar
from .compound_symbol import CompoundSymbol
import os
import re
import hashlib
import pickle
import gc

from typing import Any, Dict, Callable, Iterator, List, Optional, Tuple, Set, TypeVar, Union
from ..lex import Lexer, Token
from . import context

LOAD_OPTIMIZED = 0
GENERATE = 1
LOAD_CACHE = 2

VERSION = '1.0'
SHOW_MERGES = False


class Action(object):

    def __init__(self) -> None:
        pass

    # @abstractmethod
    def __call__(self, parser: "Parser") -> Callable[[Production], None]:
        raise NotImplementedError


class _DirectAction(Action):

    def __init__(self, action_name: str) -> None:
        Action.__init__(self)
        self._action_name = action_name

    def __call__(self, parser: "Parser") -> Callable[[Production], None]:
        return getattr(parser, self._action_name)


class _AcceptAction(Action):

    def __init__(self) -> None:
        Action.__init__(self)

    def __call__(self, parser: "Parser") -> Callable[[Production], None]:
        return parser.accept


class MergeAction(object):
    class MergeCall(object):

        def __init__(self, call: Callable[..., Any], arguments: Tuple[str, ...], result: str) -> None:
            self._call = call
            self._arguments = dict((a, []) for a in arguments)  # type: Dict[str, List[Any]]
            self._result = result

        def __call__(self, **kw: List[Any]) -> Any:
            arguments = dict(self._arguments)
            for a, v in kw.items():
                arguments[a] = v
            return self._call(**arguments)

    def __init__(
            self, method_name: str, result_name: str, filename: str, lineno: int, arguments: Tuple[str, ...]
    ) -> None:
        self._method_name = method_name
        self._result = result_name
        self._filename = filename
        self._lineno = lineno
        self._arguments = arguments

    def __call__(self, parser: "Parser") -> "MergeAction.MergeCall":
        return MergeAction.MergeCall(getattr(parser, self._method_name), self._arguments, self._result)


class Parser(object):
    AcceptAction = _AcceptAction

    def __init__(self, lexer: Lexer, start_symbol: str, temp_directory: str, mode: int = LOAD_CACHE) -> None:
        self._lexer = lexer

        if mode == LOAD_OPTIMIZED:
            self._grammar = self._load_table(temp_directory)
        else:
            h = hashlib.md5()
            h.update(VERSION.encode())
            h.update((SHOW_MERGES and 'True' or 'False').encode())
            for terminal in self._lexer._terminals:
                h.update(terminal.encode())
            for rule_action in dir(self):
                action = getattr(self, rule_action)
                for rule_string, _, _ in getattr(action, 'rules', []):
                    h.update(rule_string.encode())
                for merge_string in getattr(action, 'merge', []):
                    h.update(merge_string.encode())
                for signature in getattr(action, 'merge_signature', [[], [], []])[2]:
                    h.update(signature.encode())
                h.update(getattr(action, 'merge_result', rule_action).encode())
            if mode == LOAD_CACHE:
                try:
                    self._grammar = self._load_table(temp_directory)
                except Exception:
                    generate = True
                else:
                    generate = self._grammar._hash != h.hexdigest()
            else:
                generate = True
            if generate:
                self._grammar = self._generate_table(h.hexdigest(), start_symbol, temp_directory)

    def _load_table(self, output_directory: str) -> Grammar:
        with open(os.path.join(output_directory, self.__class__.__name__ + '.tbl'), 'rb') as table_file:
            return pickle.load(table_file)

    def _generate_table(self, rule_hash: str, start_symbol: str, temp_directory: str) -> Grammar:
        rules = []  # type: List[Tuple[str, Action, List[str], List[Tuple[str, List[str], int]], str, int]]
        merges = {}  # type: Dict[str, List[Tuple[str, MergeAction, Tuple[str, ...]]]]

        for rule_action in dir(self):
            action = getattr(self, rule_action)
            for rule_string, filename, lineno in getattr(action, 'rules', []):
                rules += _parse_rule(rule_string, rule_action, filename, lineno)
            signature = getattr(action, 'merge_signature', None)  # type: Optional[Tuple[str, int, Tuple[str, ...]]]

            if signature is not None:
                merge_result = getattr(action, 'merge_result', rule_action)
                for symbol in getattr(action, 'merge', []):
                    action = (
                        merge_result, MergeAction(rule_action, merge_result, signature[0], signature[1],
                                                  signature[2]), signature[2]
                    )
                    try:
                        merges[symbol].append(action)
                    except KeyError:
                        merges[symbol] = [action]

        grammar = Grammar(
            self.__class__.__name__, rule_hash, self._lexer._terminals, rules, merges, start_symbol, self,
            temp_directory, SHOW_MERGES
        )
        with open(os.path.join(temp_directory, self.__class__.__name__ + '.tbl'), 'wb') as table_file:
            pickle.dump(grammar, table_file, protocol=-1)
        return self._load_table(temp_directory)

    def symbol_name(self, token: Token) -> str:
        return self._grammar._name_map[token._id]

    def parse_debug(self, filename: str) -> List[Any]:
        name_map = self._grammar._name_map
        action_table = self._grammar._action_table
        goto_table = self._grammar._goto_table

        def _merge_dict(merge):
            # type: (Dict[str, Grammar.Merge]) -> Dict[str, MergeAction.MergeCall]
            result = {}
            for key, value in merge.items():
                result[key] = value._action(self)
            return result

        rules = [(r[0], r[1], r[2](self), _merge_dict(r[3])) for r in self._grammar._rules]

        RootOperation = context.RootOperation
        InputToken = context.InputToken
        GoTo = context.GoTo
        Reduce = context.Reduce
        Split = context.Split
        SplitContext = context.SplitContext
        Merge = context.Merge
        ParseError = context.ParseError
        InputOperation = Union[
            context.RootOperation,
            context.GoTo,
            context.Split
        ]

        root_operations = [RootOperation(context.State(None, 0), None)]

        def get_actions(
                operation: Union[context.RootOperation, context.GoTo],
                actions: Tuple[Tuple[int, Optional[str]], ...]
        ) -> Iterator[Tuple[InputOperation, int]]:
            action_count = len(actions)
            if action_count > 1:
                split_context = SplitContext(action_count)
                return ((Split(operation, split_context, str(name), operation._state._depth), action) for action, name
                        in
                        actions)
            else:
                return ((operation, action[0]) for action in actions)

        recovery_operations = []  # type: List[Union[context.RootOperation, context.GoTo]]
        tokens = self._lexer.input(filename, True)
        process_error = False
        for token in tokens:
            while True:
                # print(len(root_operations))
                # print(token.text())
                operations = [o for o in root_operations]  # type: List[Union[context.RootOperation, context.GoTo]]
                root_operations = []
                next_operations = []  # type: List[context.GoTo]
                merges = {}  # type: Dict[context.SplitContext, Dict[Tuple[context.State, int, Callable[..., Any]], context.Merge]]
                merge_opportunities = {}  # type: Dict[Tuple[context.SplitContext, int, context.State, int], List[Tuple[Union[context.Merge, context.Reduce], str]]]

                while operations:
                    parent = operations.pop(-1)
                    actions = action_table[parent._state._state_id].get(token._id, tuple())
                    action_count = len(actions)
                    if action_count == 0:
                        recovery_operations.append(parent)
                        del parent
                    else:
                        for input_operation, action in get_actions(parent, actions):
                            if action < 0:
                                target_state, arguments, callback, merge_rules = rules[-action - 1]
                                operation = Reduce(input_operation, target_state, len(arguments),
                                                   callback)  # type: Union[context.Reduce, context.Merge]
                                # merge
                                depth = operation._state._depth
                                split_parent = operation  # type: Union[context.Reduce, context.Merge, context.SplitInfo]
                                split = operation._split
                                found = False
                                while split:
                                    split_context = split._context
                                    if split_context._ref_count == 1:
                                        split_parent._split = split._split
                                        split = split._split
                                        continue
                                    elif depth <= split._min_depth:
                                        split._min_depth = depth
                                        try:
                                            merge_call = merge_rules[split._name]
                                        except KeyError:
                                            try:
                                                merge_opportunities[
                                                    (split_context, target_state, operation._state, depth)].append(
                                                    (operation, split._name))
                                            except KeyError:
                                                merge_opportunities[
                                                    (split_context, target_state, operation._state, depth)] = [
                                                    (operation, split._name)
                                                ]
                                            split_parent = split
                                            split = split._split
                                            continue
                                        else:
                                            try:
                                                merge_dict = merges[split_context]
                                            except KeyError:
                                                merge_dict = {}
                                                merges[split_context] = merge_dict
                                            try:
                                                merge = merge_dict[(operation._state, target_state, merge_call._call)]
                                            except KeyError:
                                                operation = Merge(operation, split, merge_call)
                                                merge_dict[
                                                    (operation._state, target_state, merge_call._call)] = operation
                                                assert operation._split is not None
                                                split_parent = operation._split
                                                split = split._split
                                                del merge_dict
                                            else:
                                                merge.add_predecessor(operation, split)
                                                found = True
                                                del merge
                                                del merge_dict
                                                break
                                    else:
                                        break
                                del split_parent
                                del split
                                if not found:
                                    # goto symbol, then loop back for another round
                                    operations.append(
                                        GoTo(operation, goto_table[operation._state._state_id][target_state]))
                                del operation
                                del input_operation
                            else:
                                next_operations.append(GoTo(context.InputToken(input_operation, token), action))
                                del input_operation
                        del parent

                for (split_context, _, state, _), ops in merge_opportunities.items():
                    if len(ops) > 1:
                        reduced_ops = []
                        for reduce_op, name in ops:
                            try:
                                reduce_op.run_debug()
                            except ParseError:
                                pass
                            else:
                                assert reduce_op._debug_value is not None
                                reduced_ops.append((reduce_op._debug_value, name))
                        if len(reduced_ops) > 1:
                            print('potential merge:')
                            for debug_sym, name in reduced_ops:
                                print('\u250f %s\n\u2503 %s' % (name, '\u2501' * len(name)))
                                debug_sym.debug_print(self._grammar._name_map, '\u2503 ', '\u2503 ')
                                print('\u2517')
                        print('')

                del merges
                for op in next_operations:
                    try:
                        op.run_debug()
                    except ParseError as error:
                        # error returns the last GoTo/Root operation that succeeded
                        recovery_operations += error._recovery_operations
                    else:
                        root_operations.append(RootOperation(op._state, op._split))
                    del op

                next_operations.clear()
                # break to get a new token
                if root_operations:
                    recovery_operations.clear()
                    if process_error:
                        # swallow tokens until one can be used
                        process_error = False
                        while True:
                            try:
                                token = next(tokens)
                            except StopIteration:
                                # woops, fatal error
                                return []
                            else:
                                tentative_roots = root_operations
                                root_operations = []
                                for tentative_op in tentative_roots:
                                    if token._id in action_table[tentative_op._state._state_id]:
                                        root_operations.append(tentative_op)
                                del tentative_op
                                if root_operations:
                                    # found some contexts that were willing to process this token, resume
                                    del tentative_roots
                                    break
                                # no operation would handle this token, throw it away abd get a new one
                                root_operations = tentative_roots
                                del tentative_roots
                        continue
                    else:
                        break

                # Syntax error: try to recover
                # first, flatten all operations
                recovery_root_operations = [RootOperation(recovery_operation._state, recovery_operation._split) for
                                            recovery_operation in recovery_operations]
                recovery_operations.clear()

                # find all grammar rules that were being parsed
                current_rules = set()
                for recovery_operation in recovery_root_operations:
                    states = [(recovery_operation._state._state_id, 0)]
                    seen_states = set()
                    while states:
                        state_id, depth = states.pop(0)
                        for actions in action_table[state_id].values():
                            for action, _ in actions:
                                if action < 0:
                                    rule = rules[-action - 1]
                                    if len(rule[1]) > depth:
                                        current_rules.add(self._grammar._name_map[rule[0]])
                                else:
                                    if action not in seen_states:
                                        seen_states.add(action)
                                        states.append((action, depth + 1))
                        for dest in goto_table[state_id].values():
                            if dest not in seen_states:
                                seen_states.add(dest)
                                states.append((dest, depth + 1))

                # print error message
                self.error(token, current_rules)

                # replace current token by an error token
                error_token = token.duplicate()
                self._lexer.set_token_type(error_token, '#error')
                process_error = True

                # rewind all ops to a state where they can handle the error token.
                # discard duplicate contexts
                seen = set()
                while recovery_root_operations:
                    recovery_operation = recovery_root_operations.pop(-1)
                    while recovery_operation._state != recovery_operation._state._parent:
                        if recovery_operation._state in seen:
                            break
                        seen.add(recovery_operation._state)
                        actions = action_table[recovery_operation._state._state_id].get(error_token._id, tuple())
                        if actions:
                            root_operations.append(recovery_operation)
                            break
                        recovery_operation._state = recovery_operation._state._parent
                    del recovery_operation
                if root_operations:
                    # resume, using the error token
                    token = error_token
                    continue
                # no recovery action at this stage; we can only exit
                return []
        results = []  # type: List[Any]
        #
        # print(len(root_operations))
        for accepted_operation in root_operations:
            actions = action_table[accepted_operation._state._state_id].get(-1, tuple())
            if len(actions) == 1:
                for action, _ in actions:
                    rule = rules[-action - 1]
                    results.append(rule[2](Production(accepted_operation._state, len(rule[1]))))
                    debug_values = []
                    state = accepted_operation._state
                    for _ in range(0, len(rule[1])):
                        assert state._debug_value is not None
                        debug_values.append(state._debug_value)
                        state = state._parent
                    CompoundSymbol(rule[0], (0, 0), debug_values[::-1]).debug_print(name_map)
        if results:
            return results
        else:
            raise SyntaxError('unexpected end of file')

    def parse_opt(self, filename: str) -> List[Any]:
        name_map = self._grammar._name_map
        action_table = self._grammar._action_table
        goto_table = self._grammar._goto_table

        def _merge_dict(merge):
            # type: (Dict[str, Grammar.Merge]) -> Dict[str, MergeAction.MergeCall]
            result = {}
            for key, value in merge.items():
                result[key] = value._action(self)
            return result

        rules = [(r[0], r[1], r[2](self), _merge_dict(r[3])) for r in self._grammar._rules]

        RootOperation = context.RootOperation
        InputToken = context.InputToken
        GoTo = context.GoTo
        Reduce = context.Reduce
        Split = context.Split
        SplitContext = context.SplitContext
        Merge = context.Merge
        ParseError = context.ParseError
        InputOperation = Union[
            context.RootOperation,
            context.GoTo,
            context.Split
        ]

        root_operations = [RootOperation(context.State(None, 0), None)]

        def get_actions(
                operation: Union[context.RootOperation, context.GoTo],
                actions: Tuple[Tuple[int, Optional[str]], ...]
        ) -> Iterator[Tuple[InputOperation, int]]:
            action_count = len(actions)
            if action_count > 1:
                split_context = SplitContext(action_count)
                return ((Split(operation, split_context, str(name), operation._state._depth), action) for action, name
                        in
                        actions)
            else:
                return ((operation, action[0]) for action in actions)

        recovery_operations = []  # type: List[Union[context.RootOperation, context.GoTo]]
        tokens = self._lexer.input(filename, True)
        process_error = False
        for token in tokens:
            while True:
                # print(len(root_operations))
                # print(token.text())
                operations = [o for o in root_operations]  # type: List[Union[context.RootOperation, context.GoTo]]
                root_operations = []
                next_operations = []  # type: List[context.GoTo]
                merges = {}  # type: Dict[context.SplitContext, Dict[Tuple[context.State, int, Callable[..., Any]], context.Merge]]

                while operations:
                    parent = operations.pop(-1)
                    actions = action_table[parent._state._state_id].get(token._id, tuple())
                    action_count = len(actions)
                    if action_count == 0:
                        recovery_operations.append(parent)
                        del parent
                    else:
                        for input_operation, action in get_actions(parent, actions):
                            if action < 0:
                                target_state, arguments, callback, merge_rules = rules[-action - 1]
                                operation = Reduce(input_operation, target_state, len(arguments),
                                                   callback)  # type: Union[context.Reduce, context.Merge]
                                # merge
                                depth = operation._state._depth
                                split_parent = operation  # type: Union[context.Reduce, context.Merge, context.SplitInfo]
                                split = operation._split
                                found = False
                                while split:
                                    split_context = split._context
                                    if split_context._ref_count == 1:
                                        split_parent._split = split._split
                                        split = split._split
                                        continue
                                    elif depth <= split._min_depth:
                                        split._min_depth = depth
                                        try:
                                            merge_call = merge_rules[split._name]
                                        except KeyError:
                                            split_parent = split
                                            split = split._split
                                            continue
                                        else:
                                            try:
                                                merge_dict = merges[split_context]
                                            except KeyError:
                                                merge_dict = {}
                                                merges[split_context] = merge_dict
                                            try:
                                                merge = merge_dict[(operation._state, target_state, merge_call._call)]
                                            except KeyError:
                                                operation = Merge(operation, split, merge_call)
                                                merge_dict[
                                                    (operation._state, target_state, merge_call._call)] = operation
                                                assert operation._split is not None
                                                split_parent = operation._split
                                                split = split._split
                                                del merge_dict
                                            else:
                                                merge.add_predecessor(operation, split)
                                                found = True
                                                del merge
                                                del merge_dict
                                                break
                                    else:
                                        break
                                del split_parent
                                del split
                                if not found:
                                    # goto symbol, then loop back for another round
                                    operations.append(
                                        GoTo(operation, goto_table[operation._state._state_id][target_state]))
                                del operation
                                del input_operation
                            else:
                                next_operations.append(GoTo(context.InputToken(input_operation, token), action))
                                del input_operation
                        del parent

                del merges
                for op in next_operations:
                    try:
                        op.run()
                    except ParseError as error:
                        # error returns the last GoTo/Root operation that succeeded
                        recovery_operations += error._recovery_operations
                    else:
                        root_operations.append(RootOperation(op._state, op._split))
                    del op

                next_operations.clear()
                # break to get a new token
                if root_operations:
                    recovery_operations.clear()
                    if process_error:
                        # swallow tokens until one can be used
                        process_error = False
                        while True:
                            try:
                                token = next(tokens)
                            except StopIteration:
                                # woops, fatal error
                                return []
                            else:
                                tentative_roots = root_operations
                                root_operations = []
                                for tentative_op in tentative_roots:
                                    if token._id in action_table[tentative_op._state._state_id]:
                                        root_operations.append(tentative_op)
                                del tentative_op
                                if root_operations:
                                    # found some contexts that were willing to process this token, resume
                                    del tentative_roots
                                    break
                                # no operation would handle this token, throw it away abd get a new one
                                root_operations = tentative_roots
                                del tentative_roots
                        continue
                    else:
                        break

                # Syntax error: try to recover
                # first, flatten all operations
                recovery_root_operations = [RootOperation(recovery_operation._state, recovery_operation._split) for
                                            recovery_operation in recovery_operations]
                recovery_operations.clear()

                # find all grammar rules that were being parsed
                current_rules = set()
                for recovery_operation in recovery_root_operations:
                    states = [(recovery_operation._state._state_id, 0)]
                    seen_states = set()
                    while states:
                        state_id, depth = states.pop(0)
                        for actions in action_table[state_id].values():
                            for action, _ in actions:
                                if action < 0:
                                    rule = rules[-action - 1]
                                    if len(rule[1]) > depth:
                                        current_rules.add(self._grammar._name_map[rule[0]])
                                else:
                                    if action not in seen_states:
                                        seen_states.add(action)
                                        states.append((action, depth + 1))
                        for dest in goto_table[state_id].values():
                            if dest not in seen_states:
                                seen_states.add(dest)
                                states.append((dest, depth + 1))

                # print error message
                self.error(token, current_rules)

                # replace current token by an error token
                error_token = token.duplicate()
                self._lexer.set_token_type(error_token, '#error')
                process_error = True

                # rewind all ops to a state where they can handle the error token.
                # discard duplicate contexts
                seen = set()
                while recovery_root_operations:
                    recovery_operation = recovery_root_operations.pop(-1)
                    while recovery_operation._state != recovery_operation._state._parent:
                        if recovery_operation._state in seen:
                            break
                        seen.add(recovery_operation._state)
                        actions = action_table[recovery_operation._state._state_id].get(error_token._id, tuple())
                        if actions:
                            root_operations.append(recovery_operation)
                            break
                        recovery_operation._state = recovery_operation._state._parent
                    del recovery_operation
                if root_operations:
                    # resume, using the error token
                    token = error_token
                    continue
                # no recovery action at this stage; we can only exit
                return []
        results = []  # type: List[Any]
        #
        # print(len(root_operations))
        for accepted_operation in root_operations:
            actions = action_table[accepted_operation._state._state_id].get(-1, tuple())
            if len(actions) == 1:
                for action, _ in actions:
                    rule = rules[-action - 1]
                    results.append(rule[2](Production(accepted_operation._state, len(rule[1]))))
        if results:
            return results
        else:
            raise SyntaxError('unexpected end of file')

    def parse(self, filename: str, debug: bool = False) -> List[Any]:
        if debug:
            return self.parse_debug(filename)
        else:
            return self.parse_opt(filename)

    def accept(self, p: Production) -> Any:
        return p[0]

    def error(self, token: Token, current_rules: Set[str]) -> None:
        filename, position, _ = self._lexer.text_position(token.position)
        print(
            '%s(%d:%d): Syntax error at token %s' %
            (filename, position[0], position[1], self._grammar._name_map[token._id])
        )
        if current_rules:
            print('  when parsing %s' % ', '.join(sorted(current_rules)))


_id = r'(?:([a-zA-Z_\-#][a-zA-Z_\-0-9#]*))'
_value = r'[a-zA-Z_\-0-9]+(:?\s*,\s*[a-zA-Z_\-0-9]+)*'
_single_quote = r"(?:'([^']*)')"
_double_quote = r'(?:"([^"]*)")'

_rule_id = re.compile(r'\s*(?:%s(\??)|%s(\??)|%s(\??))' % (_id, _single_quote, _double_quote), re.MULTILINE)
_rule_annotation = re.compile(r'\s*(:)\s*|\s*\[\s*%s\s*(\:\s*%s\s*)?\]' % (_id, _value), re.MULTILINE)
_production = re.compile(
    r'%s(\??)\s*|%s(\??)\s*|%s(\??)\s*|(\|)\s*|(\$)\s*|($)|\[\s*%s\s*(\:\s*%s\s*)?\]\s*' %
    (_id, _single_quote, _double_quote, _id, _value), re.MULTILINE
)


def _parse_rule(rule_string: str, action: str, filename: str,
                lineno: int) -> List[Tuple[str, Action, List[str], List[Tuple[str, List[str], int]], str, int]]:
    result = []  # type: List[Tuple[str, Action, List[str], List[Tuple[str, List[str], int]], str, int]]

    if rule_string:
        m = _rule_id.match(rule_string)
        if m is None:
            raise SyntaxError('unable to parse rule', (filename, lineno, 0, rule_string))
        assert m.lastindex is not None
        id = m.group(m.lastindex - 1) + m.group(m.lastindex)

        annotations = []  # type: List[Tuple[str, List[str], int]]
        while m is not None:
            parse_start = m.end()
            m = _rule_annotation.match(rule_string, m.end())
            if m is None:
                raise SyntaxError('unable to parse rule', (filename, lineno, parse_start, rule_string))
            if m.lastindex == 1:  # :
                break
            elif m.lastindex == 2:  # annotation
                annotation = m.group(2)
                annotations.append((annotation, [], -1))
            elif m.lastindex == 3:  # annotation=value
                annotation = m.group(2)
                values = [v.strip() for v in m.group(3)[1:].split(',')]
                annotations.append((annotation, values, -1))

        while True:
            production = (
                (_DirectAction(action), [], annotations[:])
            )  # type: Tuple[Action, List[str], List[Tuple[str, List[str], int]]]

            while m is not None:
                parse_start = m.end()
                m = _production.match(rule_string, m.end())
                if m is None:
                    raise SyntaxError('unable to parse rule', (filename, lineno, parse_start, rule_string))
                assert m.lastindex is not None
                if m.lastindex < 7:
                    token = m.group(m.lastindex - 1) + m.group(m.lastindex)
                    production[1].append(token)
                    continue
                elif m.lastindex == 7:  # |
                    result.append((id, production[0], production[1], production[2], filename, lineno))
                    break
                elif m.lastindex == 8:  # ;
                    result.append((id, production[0], production[1], production[2], filename, lineno))
                    rule_string = rule_string[m.end():]
                    if rule_string:
                        m = _rule_id.match(rule_string)
                        if m is None:
                            raise SyntaxError('unable to parse rule', (filename, lineno, 0, rule_string))
                        assert m.lastindex is not None
                        id = m.group(m.lastindex - 1) + m.group(m.lastindex)

                        annotations = []
                        while m is not None:
                            parse_start = m.end()
                            m = _rule_annotation.match(rule_string, m.end())
                            if m is None:
                                raise SyntaxError('unable to parse rule', (filename, lineno, parse_start, rule_string))
                            if m.lastindex == 1:  # :
                                break
                            elif m.lastindex == 2:  # annotation
                                annotation = m.group(2)
                                annotations.append((annotation, [], -1))
                            elif m.lastindex == 3:  # annotation=value
                                annotation = m.group(2)
                                values = [v.strip() for v in m.group(3)[1:].split(',')]
                                annotations.append((annotation, values, -1))
                        break
                    else:
                        return result
                elif m.lastindex == 9:  # $
                    result.append((id, production[0], production[1], production[2], filename, lineno))
                    return result
                elif m.lastindex == 10:  # annotation
                    annotation = m.group(10)
                    production[2].append((annotation, [], len(production[1])))
                elif m.lastindex == 11:  # annotation=value
                    annotation = m.group(10)
                    values = [v.strip() for v in m.group(11)[1:].split(',')]
                    production[2].append((annotation, values, len(production[1])))

    return result


T = TypeVar('T', bound=Parser)


def merge(rule_name: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
    def attach(method: Callable[..., None]) -> Callable[..., None]:
        if not hasattr(method, 'merge'):
            setattr(method, 'merge', [])

        code = method.__code__

        if getattr(code, 'co_kwonlyargcount', 0) > 0:
            raise SyntaxError('Invalid merge signature', (code.co_filename, code.co_firstlineno, 0, ''))
        if getattr(code, 'co_posonlyargcount', 0) > 0:
            raise SyntaxError('Invalid merge signature', (code.co_filename, code.co_firstlineno, 0, ''))
        if getattr(method, '__defaults__') is not None:
            raise SyntaxError(
                'Merge method should not have default arguments', (code.co_filename, code.co_firstlineno, 0, '')
            )
        argument_count = code.co_argcount
        argument_names = code.co_varnames[1:argument_count]
        setattr(method, 'merge_signature', (code.co_filename, code.co_firstlineno, tuple(a for a in argument_names)))
        getattr(method, 'merge').append(rule_name)
        return method

    return attach


def merge_result(variable_name: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
    def attach(method: Callable[..., None]) -> Callable[..., None]:
        if not hasattr(method, 'merge_result'):
            setattr(method, 'merge_result', variable_name)

        return method

    return attach


def rule(rule_string: str) -> Callable[[Callable[[T, Production], None]], Callable[[T, Production], None]]:
    def attach(method: Callable[[T, Production], None]) -> Callable[[T, Production], None]:
        if not hasattr(method, 'rules'):
            setattr(method, 'rules', [])
        code = method.__code__
        getattr(method, 'rules').append((rule_string, code.co_filename, code.co_firstlineno))
        return method

    return attach


def error_handler(method: Callable[[T, Token, Set[str]], None]) -> Callable[[T, Token, Set[str]], None]:
    setattr(Parser, 'error', method)
    return method
