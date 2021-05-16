from .production import Production
from .grammar import Grammar
from ..lex import Token
from be_typing import TYPE_CHECKING, TypeVar
from abc import abstractmethod
import os
import re
try:
    import cPickle as pickle
except ImportError:
    import pickle  # type: ignore


class Parser:
    class Stack:
        def __init__(self, stack, parent=None):
            # type: (List[Symbol], Optional[Parser.Stack]) -> None
            self._parent = parent
            self._stack = []   # type: List[Symbol]

        def __eq__(self, other):
            # type: (object) -> bool
            if isinstance(other, Parser.Stack):
                if self._parent == other._parent and len(self._stack) == len(other._stack):
                    for i1, i2 in zip(self._stack, other._stack):
                        if i1._id != i2._id:
                            break
                    else:
                        return True
            return False

        def clone(self):
            # type: () -> Parser.Stack
            return Parser.Stack(self._stack[:], self)

        def shift(self, symbol):
            # type: (Symbol) -> None
            self._stack.append(symbol)

        def reduce(self, rule):
            # type: (Grammar.Rule) -> None
            prod_len = len(rule._production)
            prod = self._stack[-prod_len:]
            self._stack[-prod_len:] = [Production(rule._id, rule._name, prod, rule._action)]

    class Action:
        def __init__(self):
            # type: () -> None
            pass

        @abstractmethod
        def __call__(self, parser):
            # type: (Parser) -> Callable[[Production], None]
            raise NotImplementedError

    class DirectAction(Action):
        def __init__(self, action_name):
            # type: (str) -> None
            Parser.Action.__init__(self)
            self._action_name = action_name

        def __call__(self, parser):
            # type: (Parser) -> Callable[[Production], None]
            return getattr(parser, self._action_name)

    class OptionalAction(Action):
        def __init__(self, action, optional_index):
            # type: (Parser.Action, int) -> None
            Parser.Action.__init__(self)
            self._action = action
            self._index = optional_index

        def __call__(self, parser):
            # type: (Parser) -> Callable[[Production], None]
            action = self._action(parser)

            def call(production):
                # type: (Production) -> Any
                production._insert(self._index, Token(1, '<empty>', production._position, None, []))
                action(production)

            return call

    class AcceptAction(Action):
        def __init__(self):
            # type: () -> None
            Parser.Action.__init__(self)

        def __call__(self, parser):
            # type: (Parser) -> Callable[[Production], None]
            return parser.accept

    def __init__(self, lexer, start_symbol, tab_filename):
        # type: (Lexer, str, str) -> None
        self._lexer = lexer

        rules = []     # type: List[Tuple[str, Parser.Action, List[str]]]
        for rule_action in dir(self):
            action = getattr(self, rule_action)
            for rule_string in getattr(action, 'rules', []):
                rules += _parse_rule(rule_string, rule_action)

        grammar = Grammar(
            self._lexer._terminals, rules, start_symbol, self, tab_filename,
            os.path.splitext(tab_filename)[0] + '.log'
        )

    def parse(self, filename):
        # type: (str) -> Any
        self._lexer.input(filename)

        s = Parser.Stack([])
        for token in self._lexer.token():
            s.shift(token)

    def accept(self, p):
        # type: (Production) -> None
        p[0] = p[1]


_id = r'([a-zA-Z_\-][a-zA-Z_\-0-9]*)'
_single_quote = r"(?:'([^']*)')"
_double_quote = r'(?:"([^"]*)")'

_rule_id = re.compile(r'\s*%s\s*:\s*' % _id, re.MULTILINE)
_production = re.compile(
    r'%s(\??)\s*|%s(\??)\s*|%s(\??)\s*|(\|)\s*|(;)\s*|($)' % (_id, _single_quote, _double_quote), re.MULTILINE
)


def _parse_rule(rule_string, action):
    # type: (str, str) -> List[Tuple[str, Parser.Action, List[str]]]
    result = []    # type: List[Tuple[str, Parser.Action, List[str]]]

    if rule_string:
        m = _rule_id.match(rule_string)
        if m is None:
            raise SyntaxError()
        id = m.group(1)

        while True:
            productions = [(Parser.DirectAction(action), [])] # type: List[Tuple[Parser.Action, List[str]]]
            index = 0
            while m is not None:
                m = _production.match(rule_string, m.end())
                if m is None:
                    raise SyntaxError()
                assert m.lastindex is not None
                if m.lastindex < 7:
                    for p in productions:
                        p[1].append(m.group(m.lastindex - 1))
                    if m.group(m.lastindex) == '?':
                        productions += [(Parser.OptionalAction(p[0], index), p[1][:-1]) for p in productions]
                    continue
                elif m.lastindex == 7:                        # |
                    for p in productions:
                        result.append((id, p[0], p[1]))
                    break
                elif m.lastindex == 8:                        # ;
                    for p in productions:
                        result.append((id, p[0], p[1]))
                    rule_string = rule_string[m.end():]
                    if rule_string:
                        m = _rule_id.match(rule_string)
                        if m is None:
                            raise SyntaxError()
                        id = m.group(1)
                        break
                    else:
                        return result
                elif m.lastindex == 9:                        # $
                    for p in productions:
                        result.append((id, p[0], p[1]))
                    return result

    return result


T = TypeVar('T', bound=Parser)


def rule(rule_string):
    # type: (str) -> Callable[[Callable[[T, Production], None]], Callable[[T, Production], None]]
    def attach(method):
        # type: (Callable[[T, Production], None]) -> Callable[[T, Production], None]
        if not hasattr(method, 'rules'):
            setattr(method, 'rules', [])
        getattr(method, 'rules').append(rule_string)
        return method

    return attach


if TYPE_CHECKING:
    from typing import Any, Callable, List, Optional, Tuple
    from ..lex import Lexer
    from ..symbol import Symbol