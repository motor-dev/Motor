from .production import Production
from .grammar import Grammar
from .context import Context, Merge, SplitContext
from motor_typing import TYPE_CHECKING, TypeVar
import os
import re
import hashlib
import zlib
import base64
try:
    import cPickle as pickle   # type: ignore
except ImportError:
    import pickle              # type: ignore

LOAD_OPTIMIZED = 0
GENERATE = 1
LOAD_CACHE = 2

VERSION = '1.0'
SHOW_MERGES = False


class Action(object):

    def __init__(self):
        # type: () -> None
        pass

    #@abstractmethod
    def __call__(self, parser):
        # type: (Parser) -> Callable[[Production], None]
        raise NotImplementedError


class _DirectAction(Action):

    def __init__(self, action_name):
        # type: (str) -> None
        Action.__init__(self)
        self._action_name = action_name

    def __call__(self, parser):
        # type: (Parser) -> Callable[[Production], None]
        return getattr(parser, self._action_name)


class _AcceptAction(Action):

    def __init__(self):
        # type: () -> None
        Action.__init__(self)

    def __call__(self, parser):
        # type: (Parser) -> Callable[[Production], None]
        return parser.accept


class MergeAction(object):

    class MergeCall(object):

        def __init__(self, call, arguments, result):
            # type: (Callable[..., Any], Tuple[str, ...], str) -> None
            self._call = call
            self._arguments = dict((a, []) for a in arguments) # type: Dict[str, Any]
            self._result = result

        def __call__(self, **kw):
            # type: (Dict[str, Any]) -> Any
            arguments = dict(self._arguments)
            for a, v in kw.items():
                arguments[a] = v
            return self._call(**arguments)

    def __init__(self, method_name, result_name, filename, lineno, arguments):
        # type: (str, str, str, int, Tuple[str, ...]) -> None
        self._method_name = method_name
        self._result = result_name
        self._filename = filename
        self._lineno = lineno
        self._arguments = arguments

    def __call__(self, parser):
        # type: (Parser) -> MergeAction.MergeCall
        return MergeAction.MergeCall(getattr(parser, self._method_name), self._arguments, self._result)


class Parser(object):
    AcceptAction = _AcceptAction

    def __init__(self, lexer, start_symbol, temp_directory, output_directory, mode=LOAD_CACHE):
        # type: (Lexer, str, str, str, int) -> None
        self._lexer = lexer

        if mode == LOAD_OPTIMIZED:
            self._grammar = self._load_table(output_directory)
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
                    self._grammar = self._load_table(output_directory)
                except Exception:
                    generate = True
                else:
                    generate = self._grammar._hash != h.hexdigest()
            else:
                generate = True
            if generate:
                self._grammar = self._generate_table(h.hexdigest(), start_symbol, temp_directory, output_directory)

    def _load_table(self, output_directory):
        # type: (str) -> Grammar
        with open(os.path.join(output_directory, self.__class__.__name__ + '.tbl'), 'rb') as table_file:
            return pickle.loads(zlib.decompress(base64.b64decode(table_file.read())))

    def _generate_table(self, rule_hash, start_symbol, temp_directory, output_directory):
        # type: (str, str, str, str) -> Grammar
        rules = []                                                                                       # type: List[Tuple[str, Action, List[str], List[Tuple[str, List[str], int]], str, int]]
        merges = {}                                                                                      # type: Dict[str, List[Tuple[str, MergeAction, Tuple[str, ...]]]]
        for rule_action in dir(self):
            action = getattr(self, rule_action)
            for rule_string, filename, lineno in getattr(action, 'rules', []):
                rules += _parse_rule(rule_string, rule_action, filename, lineno)
            signature = getattr(action, 'merge_signature', None)                                         # type: Optional[Tuple[str, int, Tuple[str, ...]]]
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
        with open(os.path.join(output_directory, self.__class__.__name__ + '.tbl'), 'wb') as table_file:
            table_file.write(base64.b64encode(zlib.compress(pickle.dumps(grammar, protocol=0), 9)))
        return self._load_table(output_directory)

    def parse_debug(self, filename):
        # type: (str) -> List[Any]

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

        for token in self._lexer.input(filename):
            #print(self._grammar._name_map[token._id])
            #print(len(contexts))
            print(len(contexts))
            operations = [context.input(token) for context in contexts]

            next_contexts = []         # type: List[Operation]
            merges = {}                # type: Dict[Tuple[SplitContext, int, int, Callable[[], None]], Merge]
            merge_opportunities = {}   # type: Dict[Tuple[SplitContext, int, int, int], List[Tuple[Operation, str]]]
            recovery_contexts = []     # type: List[Operation]

            while operations:
                parent = operations.pop(-1)
                actions = action_table[parent._state].get(token._id, tuple())
                if len(actions) == 0:
                    recovery_contexts.append(parent)
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
                                                merge_op = merges[
                                                    (scontext, operation._state, sym_len, merge_action._call)]
                                            except KeyError:
                                                merge_op = Merge(operation, merge_action, name, scontext)
                                                merges[(scontext, operation._state, sym_len, merge_action._call)
                                                       ] = merge_op
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
                                            merge_opportunities[(scontext, operation._state, sym_len, rule[0])].append(
                                                (operation, name)
                                            )
                                        except KeyError:
                                            merge_opportunities[(scontext, operation._state, sym_len, rule[0])] = [
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

            for (split_context, _, _, symbol), ops in merge_opportunities.items():
                if len(ops) > 1:
                    print('potential merge:')
                    for reduce_op, name in ops:
                        print('\u250f %s\n\u2503 %s' % (name, '\u2501' * len(name)))
                        debug_sym = reduce_op.run_debug()[1]
                        debug_sym.debug_print(self._grammar._name_map, '\u2503 ', '\u2503 ')
                        print('\u2517')
                    print('')

            if len(next_contexts) == 0:
                valid_tokens = set()
                for recovery_context in recovery_contexts:
                    for production_id, _ in goto_table[recovery_context._state].items():
                        valid_tokens.add(production_id)
                position = self._lexer.text_position(token)
                print(
                    '%s(%d:%d): Syntax error at token %s' %
                    (filename, position[0][0], position[0][1], self._grammar._name_map[token._id])
                )
                print(
                    '  expected %s' %
                    ', '.join([self._grammar._name_map[production_id] for production_id in sorted(valid_tokens)])
                )
                return []
            contexts = []
            for operation in next_contexts:
                try:
                    operation.run_debug()
                except SyntaxError:
                    pass
                else:
                    contexts.append(operation._result_context)

        print(len(contexts))
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

    def parse_opt(self, filename):
        # type: (str) -> List[Any]

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

        for token in self._lexer.input(filename):
            #print(self._grammar._name_map[token._id])
            operations = [context.input(token) for context in contexts]

            next_contexts = []         # type: List[Operation]
            merges = {}                # type: Dict[Tuple[SplitContext, int, int, Callable[[], None]], Merge]
            recovery_contexts = []     # type: List[Operation]

            while operations:
                parent = operations.pop(-1)
                actions = action_table[parent._state].get(token._id, tuple())
                if len(actions) == 0:
                    recovery_contexts.append(parent)
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
                                                merge_op = merges[
                                                    (scontext, operation._state, sym_len, merge_action._call)]
                                            except KeyError:
                                                merge_op = Merge(operation, merge_action, name, scontext)
                                                merges[(scontext, operation._state, sym_len, merge_action._call)
                                                       ] = merge_op
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

            if len(next_contexts) == 0:
                valid_tokens = set()
                for recovery_context in recovery_contexts:
                    for production_id, _ in goto_table[recovery_context._state].items():
                        valid_tokens.add(production_id)
                position = self._lexer.text_position(token)
                print(
                    '%s(%d:%d): Syntax error at token %s' %
                    (filename, position[0][0], position[0][1], self._grammar._name_map[token._id])
                )
                print(
                    '  expected %s' %
                    ', '.join([self._grammar._name_map[production_id] for production_id in sorted(valid_tokens)])
                )
                return []
            contexts = []
            for operation in next_contexts:
                try:
                    operation.run()
                except SyntaxError:
                    pass
                else:
                    contexts.append(operation._result_context)

        print(len(contexts))
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

    def parse(self, filename):
        # type: (str) -> List[Any]
        return self.parse_debug(filename)

    def accept(self, p):
        # type: (Production) -> Any
        return p[0]


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


def _parse_rule(rule_string, action, filename, lineno):
    # type: (str, str, str, int) -> List[Tuple[str, Action, List[str], List[Tuple[str, List[str], int]], str, int]]
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


def merge(rule_name):
    # type: (str) -> Callable[[Callable[..., None]], Callable[..., None]]
    def attach(method):
        # type: (Callable[..., None]) -> Callable[..., None]
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


def merge_result(variable_name):
    # type: (str) -> Callable[[Callable[..., None]], Callable[..., None]]
    def attach(method):
        # type: (Callable[..., None]) -> Callable[..., None]
        if not hasattr(method, 'merge_result'):
            setattr(method, 'merge_result', variable_name)

        return method

    return attach


def rule(rule_string):
    # type: (str) -> Callable[[Callable[[T, Production], None]], Callable[[T, Production], None]]
    def attach(method):
        # type: (Callable[[T, Production], None]) -> Callable[[T, Production], None]
        if not hasattr(method, 'rules'):
            setattr(method, 'rules', [])
        code = method.__code__
        getattr(method, 'rules').append((rule_string, code.co_filename, code.co_firstlineno))
        return method

    return attach


if TYPE_CHECKING:
    from typing import Any, Dict, Callable, List, Optional, Tuple, Set
    from ..lex import Lexer
    from .context import Operation
