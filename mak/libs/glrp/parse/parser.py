from .production import Production
from .grammar import Grammar
from .context import Context
from motor_typing import TYPE_CHECKING, TypeVar
import os
import sys
import re
import hashlib
import zlib
import base64
try:
    import cPickle as pickle
except ImportError:
    import pickle  # type: ignore

LOAD_OPTIMIZED = 0
GENERATE = 1
LOAD_CACHE = 2

VERSION = '0.22'


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
            for rule_action in dir(self):
                action = getattr(self, rule_action)
                for rule_string, _, _ in getattr(action, 'rules', []):
                    h.update(rule_string.encode())
                for merge_string in getattr(action, 'merge', []):
                    h.update(merge_string.encode())
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
        rules = []                                               # type: List[Tuple[str, Action, List[str], List[Tuple[str, List[str], int]], str, int]]
        merges = {}                                              # type: Dict[str, List[Tuple[str, Dict[str, None]]]]
        for rule_action in dir(self):
            action = getattr(self, rule_action)
            for rule_string, filename, lineno in getattr(action, 'rules', []):
                rules += _parse_rule(rule_string, rule_action, filename, lineno)
            signature = getattr(action, 'merge_signature', None) # type: Optional[Dict[str, None]]
            if signature is not None:
                for symbol in getattr(action, 'merge', []):
                    try:
                        merges[symbol].append((rule_action, signature))
                    except KeyError:
                        merges[symbol] = [(rule_action, signature)]

        grammar = Grammar(
            self.__class__.__name__, rule_hash, self._lexer._terminals, rules, merges, start_symbol, self,
            temp_directory
        )
        with open(os.path.join(output_directory, self.__class__.__name__ + '.tbl'), 'wb') as table_file:
            table_file.write(base64.b64encode(zlib.compress(pickle.dumps(grammar, protocol=0), 9)))
        return self._load_table(output_directory)

    def parse(self, filename):
        # type: (str) -> Any
        self._lexer.input(filename)

        contexts = [Context(None, "'")]

        action_table = self._grammar._action_table
        goto_table = self._grammar._goto_table
        rules = [(r[0], r[1], r[2](self)) for r in self._grammar._rules]
        prev_position = 0

        for token in self._lexer.token():
            for context in contexts:
                actions = action_table[context._state_stack[-1]].get(token._id, tuple())
                if len(actions) != 1:
                    # TODO
                    pass
                else:
                    for action, token_action in actions[:1]:
                        while action < 0:
                            rule = rules[-action - 1]
                            symbol = rule[0]
                            symbol_count = len(rule[1])
                            if symbol_count:
                                production = Production(
                                    symbol, context._sym_stack[-symbol_count]._start_position,
                                    context._sym_stack[-1]._end_position, context._sym_stack[-symbol_count:], rule[2]
                                )
                            else:
                                production = Production(symbol, prev_position, token._start_position, [], rule[2])
                            production.run()
                            if symbol_count:
                                del context._sym_stack[-symbol_count:]
                                del context._state_stack[-symbol_count:]
                            context._sym_stack.append(production)
                            context._state_stack.append(goto_table[context._state_stack[-1]][symbol])
                            actions = action_table[context._state_stack[-1]].get(token._id, tuple())
                            action, token_action = actions[0]

                        if action > 0:
                            context._sym_stack.append(token)
                            context._state_stack.append(action)
            prev_position = token._end_position
        for context in contexts:
            actions = action_table[context._state_stack[-1]].get(-1, tuple())
            if len(actions) == 1:
                for action, token_action in actions:
                    rule = rules[-action - 1]
                    symbol = rule[0]
                    production = Production(
                        symbol, context._sym_stack[0]._start_position, context._sym_stack[-1]._end_position,
                        context._sym_stack, rule[2]
                    )
                    production.run()
                return production.value
        else:
            raise SyntaxError('unexpected end of file')

    def accept(self, p):
        # type: (Production) -> None
        p[0] = p[1]


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
    # type: (str) -> Callable[[Callable[..., int]], Callable[..., int]]
    def attach(method):
        # type: (Callable[..., int]) -> Callable[..., int]
        if not hasattr(method, 'merge'):
            setattr(method, 'merge', [])

        code = method.__code__

        if sys.version_info >= (3, 0):
            if code.co_posonlyargcount > 0:
                raise SyntaxError('Invalid merge signature', (code.co_filename, code.co_firstlineno, 0, ''))
            if code.co_kwonlyargcount > 0:
                raise SyntaxError('Invalid merge signature', (code.co_filename, code.co_firstlineno, 0, ''))
        if getattr(method, '__defaults__') is not None:
            raise SyntaxError(
                'Merge method should not have default arguments', (code.co_filename, code.co_firstlineno, 0, '')
            )
        argument_count = code.co_argcount
        argument_names = code.co_varnames[1:argument_count]
        setattr(method, 'merge_signature', dict([(a, None) for a in argument_names]))
        getattr(method, 'merge').append(rule_name)
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
    from typing import Any, Dict, Callable, List, Optional, Tuple, Type
    from ..lex import Lexer
    from ..symbol import Symbol