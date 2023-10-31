from .production import Production
from .grammar import Grammar
from .context import Context, Merge, SplitContext, ParseError
from .compound_symbol import CompoundSymbol
import os
import re
import hashlib
import pickle

from typing import Any, Dict, Callable, List, Optional, Tuple, Set, TypeVar
from ..lex import Lexer, Token
from .context import Operation

LOAD_OPTIMIZED = 0
GENERATE = 1
LOAD_CACHE = 2

VERSION = '1.0'
SHOW_MERGES = False


class Action(object):

    def __init__(self) -> None:
        pass

    #@abstractmethod
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
            self._arguments = dict((a, []) for a in arguments) # type: Dict[str, Any]
            self._result = result

        def __call__(self, **kw: Dict[str, Any]) -> Any:
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
        rules = []     # type: List[Tuple[str, Action, List[str], List[Tuple[str, List[str], int]], str, int]]
        merges = {}    # type: Dict[str, List[Tuple[str, MergeAction, Tuple[str, ...]]]]

        for rule_action in dir(self):
            action = getattr(self, rule_action)
            for rule_string, filename, lineno in getattr(action, 'rules', []):
                rules += _parse_rule(rule_string, rule_action, filename, lineno)
            signature = getattr(action, 'merge_signature', None) # type: Optional[Tuple[str, int, Tuple[str, ...]]]

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
        contexts = [Context(None, None)]

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

        tokens = self._lexer.input(filename, True)
        for token in tokens:
            #print(self._grammar._name_map[token._id])
            #print(len(contexts))
            while True:
                operations = [context.input(token) for context in contexts]

                next_contexts = []       # type: List[Operation]
                merges = {}              # type: Dict[Tuple[SplitContext, int, int, int, Callable[[], None]], Merge]
                merge_opportunities = {} # type: Dict[Tuple[SplitContext, int, int, int], List[Tuple[Operation, str]]]
                recovery_operations = [] # type: List[Operation]
                recovery_contexts = []   # type: List[Context]

                while operations:
                    parent = operations.pop(-1)
                    actions = action_table[parent._state].get(token._id, tuple())
                    if len(actions) == 0:
                        recovery_operations.append(parent)
                        parent.discard()
                    else:
                        for operation, (action, _) in zip(parent.split(actions), actions):
                            if action < 0:
                                rule = rules[-action - 1]
                                operation = operation.reduce(rule)
                                end = False
                                seen = set() # type:Set[SplitContext]

                                while not end:
                                    for i, split_task in enumerate(operation._result_context._names[::-1]):
                                        sym_len = operation._result_context._sym_len
                                        scontext = split_task[0]
                                        name = split_task[1]
                                        if split_task[2] >= sym_len:
                                            operation._result_context._names[-i - 1] = (scontext, name, sym_len)
                                            if scontext in seen:
                                                continue
                                            try:
                                                merge_action = rule[3][name]
                                            except KeyError:
                                                pass
                                            else:
                                                seen.add(scontext)
                                                try:
                                                    merge_op = merges[(
                                                        scontext, rule[0], operation._state, sym_len, merge_action._call
                                                    )]
                                                except KeyError:
                                                    merge_op = Merge(operation, merge_action, name, scontext)
                                                    merges[(
                                                        scontext, rule[0], operation._state, sym_len, merge_action._call
                                                    )] = merge_op
                                                    operation = merge_op
                                                else:
                                                    merge_op.add_operation(operation, name, scontext)
                                                    end = True
                                                break
                                    else:
                                        for split_task in operation._result_context._names[::-1]:
                                            scontext = split_task[0]
                                            name = split_task[1]
                                            if split_task[2] < sym_len:
                                                break
                                            try:
                                                merge_opportunities[(scontext, rule[0], operation._state,
                                                                     sym_len)].append((operation, name))
                                            except KeyError:
                                                merge_opportunities[(scontext, rule[0], operation._state, sym_len)] = [
                                                    (operation, name)
                                                ]
                                        break
                                if not end:
                                    # goto symbol, then loop back for another round
                                    target_state = goto_table[operation._state][rule[0]]
                                    operations.append(operation.goto(target_state))
                            else:
                                operation = operation.consume_token(token, action)
                                next_contexts.append(operation)

                for (split_context, _, _, _), ops in merge_opportunities.items():
                    if len(ops) > 1:
                        reduced_ops = []
                        for reduce_op, name in ops:
                            try:
                                reduced_ops.append((reduce_op.run_debug()[1], name))
                            except ParseError:
                                pass
                        if len(reduced_ops) > 1:
                            print('potential merge:')
                            for debug_sym, name in reduced_ops:
                                print('\u250f %s\n\u2503 %s' % (name, '\u2501' * len(name)))
                                debug_sym.debug_print(self._grammar._name_map, '\u2503 ', '\u2503 ')
                                print('\u2517')
                        print('')

                if len(next_contexts) != 0:
                    contexts = []
                    for operation in next_contexts:
                        try:
                            operation.run_debug()
                        except ParseError as error:
                            operation._result_context = operation._result_context.flatten().flatten()
                            operation.undo(operation._result_context, error.recovery_operation)
                            recovery_contexts.append(operation._result_context)
                            operation.discard()
                        else:
                            contexts.append(operation._result_context)

                    # break to get a new token
                    if contexts:
                        break

                for recovery_operation in recovery_operations:
                    recovery_operation._result_context = recovery_operation._result_context.flatten()
                    try:
                        recovery_operation.run_debug()
                    except ParseError as error:
                        recovery_operation.undo(recovery_operation._result_context, error.recovery_operation)
                    recovery_contexts.append(recovery_operation._result_context.flatten())

                # Syntax error: try to recover
                current_rules = set()
                for recovery_context in recovery_contexts:
                    states = [(recovery_context._state, 0)]
                    seen_states = set([recovery_context._state])
                    while states:
                        state, depth = states.pop(0)
                        for actions in action_table[state].values():
                            for action, _ in actions:
                                if action < 0:
                                    rule = rules[-action - 1]
                                    if len(rule[1]) > depth:
                                        current_rules.add(self._grammar._name_map[rule[0]])
                                else:
                                    if action not in seen_states:
                                        seen_states.add(action)
                                        states.append((action, depth + 1))
                        for dest in goto_table[state].values():
                            if dest not in seen_states:
                                seen_states.add(dest)
                                states.append((dest, depth + 1))

                self.error(token, current_rules)

                error_token = token.duplicate()
                self._lexer.set_token_type(error_token, '#error')
                contexts = []
                for context in recovery_contexts:
                    while context._state_stack:
                        if error_token._id in action_table[context._state]:
                            action = action_table[context._state][error_token._id][0][0]
                            if action < 0:
                                rule = rules[-action - 1]
                                pop_count = len(rule[1])
                                p = Production(context, pop_count)
                                symbol = rule[2](p)
                                if pop_count:
                                    debug_sym = CompoundSymbol(rule[0], (0, 0), context._debug_stack[-pop_count:])
                                else:
                                    debug_sym = CompoundSymbol(rule[0], (0, 0), [])
                                context.reduce_debug(pop_count)
                                context.pop(pop_count)
                                context.add_prod_debug(symbol, debug_sym)
                                context.goto(goto_table[context._state][rule[0]])
                            else:
                                context.add_prod_debug(error_token, error_token)
                                context.goto(action)
                                contexts.append(context)
                                break
                        else:
                            context.reduce_debug(1)
                            context.pop(1)

                if not contexts:
                    return []
                contexts.sort(key=lambda x: x._sym_len)
                while True:
                    for context in contexts:
                        if token._id in action_table[context._state]:
                            contexts = [context]
                            break
                    else:
                        try:
                            token = next(tokens)
                        except StopIteration:
                            # reach end of file, return no result
                            return []
                        continue
                    # found a new token, go back to beginning and continue
                    break

        results = []   # type: List[Any]
        for context in contexts:
            actions = action_table[context._state].get(-1, tuple())
            if len(actions) == 1:
                for action, _ in actions:
                    rule = rules[-action - 1]
                    results.append(rule[2](Production(context, len(rule[1]))))
                    context._debug_stack[0].debug_print(name_map)
        if results:
            return results
        else:
            raise SyntaxError('unexpected end of file')

    def parse_opt(self, filename: str) -> List[Any]:
        contexts = [Context(None, None)]

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

        tokens = self._lexer.input(filename, True)
        for token in tokens:
            #print(self._grammar._name_map[token._id])
            while True:
                operations = [context.input(token) for context in contexts]

                next_contexts = []       # type: List[Operation]
                merges = {}              # type: Dict[Tuple[SplitContext, int, int, int, Callable[[], None]], Merge]
                recovery_operations = [] # type: List[Operation]
                recovery_contexts = []   # type: List[Context]

                while operations:
                    parent = operations.pop(-1)
                    actions = action_table[parent._state].get(token._id, tuple())
                    if len(actions) == 0:
                        recovery_operations.append(parent)
                        parent.discard()
                    else:
                        for operation, (action, _) in zip(parent.split(actions), actions):
                            if action < 0:
                                rule = rules[-action - 1]
                                operation = operation.reduce(rule)
                                end = False
                                seen = set() # type:Set[SplitContext]

                                while not end:
                                    sym_len = operation._result_context._sym_len
                                    for i, split_task in enumerate(operation._result_context._names[::-1]):
                                        scontext = split_task[0]
                                        name = split_task[1]
                                        if split_task[2] >= sym_len:
                                            operation._result_context._names[-i - 1] = (scontext, name, sym_len)
                                            if scontext in seen:
                                                continue
                                            try:
                                                merge_action = rule[3][name]
                                            except KeyError:
                                                pass
                                            else:
                                                seen.add(scontext)
                                                try:
                                                    merge_op = merges[(
                                                        scontext, rule[0], operation._state, sym_len, merge_action._call
                                                    )]
                                                except KeyError:
                                                    merge_op = Merge(operation, merge_action, name, scontext)
                                                    merges[(
                                                        scontext, rule[0], operation._state, sym_len, merge_action._call
                                                    )] = merge_op
                                                    operation = merge_op
                                                else:
                                                    merge_op.add_operation(operation, name, scontext)
                                                    end = True
                                                break
                                    else:
                                        break
                                if not end:
                                    # goto symbol, then loop back for another round
                                    target_state = goto_table[operation._state][rule[0]]
                                    operations.append(operation.goto(target_state))
                            else:
                                operation = operation.consume_token(token, action)
                                next_contexts.append(operation)

                if len(next_contexts) != 0:
                    contexts = []
                    for operation in next_contexts:
                        try:
                            operation.run_debug()
                        except ParseError as error:
                            operation.undo(operation._result_context, error.recovery_operation)
                            recovery_contexts.append(operation._result_context.flatten())
                        else:
                            contexts.append(operation._result_context)

                    # break to get a new token
                    if contexts:
                        break

                for recovery_operation in recovery_operations:
                    try:
                        recovery_operation.run_debug()
                    except ParseError as error:
                        recovery_operation.undo(recovery_operation._result_context, error.recovery_operation)
                        recovery_contexts.append(recovery_operation._result_context.flatten())
                    else:
                        recovery_contexts.append(recovery_operation._result_context.flatten())

                # Syntax error: try to recover
                current_rules = set()
                for recovery_context in recovery_contexts:
                    states = [(recovery_context._state, 0)]
                    seen_states = set([recovery_context._state])
                    while states:
                        state, depth = states.pop(0)
                        for actions in action_table[state].values():
                            for action, _ in actions:
                                if action < 0:
                                    rule = rules[-action - 1]
                                    if len(rule[1]) > depth:
                                        current_rules.add(self._grammar._name_map[rule[0]])
                                else:
                                    if action not in seen_states:
                                        seen_states.add(action)
                                        states.append((action, depth + 1))
                        for dest in goto_table[state].values():
                            if dest not in seen_states:
                                seen_states.add(dest)
                                states.append((dest, depth + 1))

                self.error(token, current_rules)

                error_token = token.duplicate()
                self._lexer.set_token_type(error_token, '#error')
                contexts = []
                for context in recovery_contexts:
                    while context._state_stack:
                        if error_token._id in action_table[context._state]:
                            context.add_prod(error_token)
                            context.goto(action_table[context._state][error_token._id][0][0])
                            contexts.append(context)
                            break
                        else:
                            context.reduce(1)
                            context.pop(1)

                if not contexts:
                    return []
                contexts.sort(key=lambda x: x._sym_len)
                while True:
                    for context in contexts:
                        if token._id in action_table[context._state]:
                            contexts = [context]
                            break
                    else:
                        try:
                            token = next(tokens)
                        except StopIteration:
                            # reach end of file, return no result
                            return []
                        continue
                    # found a new token, go back to beginning and continue
                    break

        results = []   # type: List[Any]
        for context in contexts:
            actions = action_table[context._state].get(-1, tuple())
            if len(actions) == 1:
                for action, _ in actions:
                    rule = rules[-action - 1]
                    results.append(rule[2](Production(context, len(rule[1]))))
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


_id = r'(?:([a-zA-Z_\-][a-zA-Z_\-0-9]*))'
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
    result = []    # type: List[Tuple[str, Action, List[str], List[Tuple[str, List[str], int]], str, int]]

    if rule_string:
        m = _rule_id.match(rule_string)
        if m is None:
            raise SyntaxError('unable to parse rule', (filename, lineno, 0, rule_string))
        assert m.lastindex is not None
        id = m.group(m.lastindex - 1) + m.group(m.lastindex)

        annotations = []               # type: List[Tuple[str, List[str], int]]
        while m is not None:
            parse_start = m.end()
            m = _rule_annotation.match(rule_string, m.end())
            if m is None:
                raise SyntaxError('unable to parse rule', (filename, lineno, parse_start, rule_string))
            if m.lastindex == 1:       # :
                break
            elif m.lastindex == 2:     # annotation
                annotation = m.group(2)
                annotations.append((annotation, [], -1))
            elif m.lastindex == 3:     # annotation=value
                annotation = m.group(2)
                values = [v.strip() for v in m.group(3)[1:].split(',')]
                annotations.append((annotation, values, -1))

        while True:
            production = (
                (_DirectAction(action), [], annotations[:])
            )                                               # type: Tuple[Action, List[str], List[Tuple[str, List[str], int]]]

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
                elif m.lastindex == 7: # |
                    result.append((id, production[0], production[1], production[2], filename, lineno))
                    break
                elif m.lastindex == 8: # ;
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
                            if m.lastindex == 1:   # :
                                break
                            elif m.lastindex == 2: # annotation
                                annotation = m.group(2)
                                annotations.append((annotation, [], -1))
                            elif m.lastindex == 3: # annotation=value
                                annotation = m.group(2)
                                values = [v.strip() for v in m.group(3)[1:].split(',')]
                                annotations.append((annotation, values, -1))
                        break
                    else:
                        return result
                elif m.lastindex == 9:             # $
                    result.append((id, production[0], production[1], production[2], filename, lineno))
                    return result
                elif m.lastindex == 10:            # annotation
                    annotation = m.group(10)
                    production[2].append((annotation, [], len(production[1])))
                elif m.lastindex == 11:            # annotation=value
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
