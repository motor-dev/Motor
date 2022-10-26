from .token import Token
from ..symbol import Symbol
import re
from motor_typing import TYPE_CHECKING, TypeVar

F = TypeVar('F', bound='Lexer')


class Lexer:
    tokens = tuple()   # type: Tuple[str,...]

    class State:

        def __init__(self, regex_list):
            # type: (List[Tuple[Pattern[str], List[Optional[Tuple[Callable[[F, Token], Optional[Token]], str, bool, int]]]]]) -> None
            self._regex = regex_list

    def __init__(self):
        # type: () -> None
        self._states = {}          # type: Dict[str, Lexer.State]
        self._state_stack = []     # type: List[Lexer.State]
        self._terminals = {'#eof': (0, False), '#mark': (1, False), '#start': (2, False), '#error': (3, False)}
        self._filename = ''
        self._lexdata = ''
        self._lexlen = 0
        self._states = _build_states(self.__class__)
        for state_name, state in self._states.items():
            for regex, lexindexfunc in state._regex:
                for token in lexindexfunc:
                    if token is not None:
                        callback, name, warn, index = token
                        self._terminals[name] = (index, warn)
        for token_name in self.tokens:
            if token_name not in self._terminals:
                self._terminals[token_name] = (len(self._terminals), True)

    def input(self, filename):
        # type: (str) -> Generator[Token, None, None]
        self._filename = filename
        with open(filename, 'r') as file:
            self._lexdata = file.read()
            self._lexlen = len(self._lexdata)
        return self._token()

    def get_token_id(self, token_type):
        # type: (str) -> int
        return self._terminals[token_type][0]

    def set_token_type(self, token, type):
        # type: (Token, str) -> Token
        token._id = self.get_token_id(type)
        return token

    def push_state(self, state):
        # type: (str) -> None
        self._state_stack.append(self._states[state])

    def pop_state(self):
        # type: () -> None
        self._state_stack.pop(-1)

    def text(self, symbol):
        # type: (Symbol) -> str
        return self._lexdata[symbol._start_position:symbol._end_position]

    def text_position(self, symbol):
        # type: (Symbol) -> Tuple[Tuple[int, int], Tuple[int, int]]
        lexdata = self._lexdata
        start_lineno = lexdata.count('\n', 0, symbol._start_position) + 1
        line_count = lexdata.count('\n', symbol._start_position, symbol._end_position)
        end_lineno = start_lineno + line_count

        if start_lineno:
            start_column = symbol._start_position - lexdata.rfind('\n', 0, symbol._start_position)
        else:
            start_column = symbol._start_position

        if line_count:
            end_column = symbol._end_position - lexdata.rfind('\n', symbol._start_position, symbol._end_position)
        else:
            end_column = start_column + symbol._end_position - symbol._start_position

        return ((start_lineno, start_column), (end_lineno, end_column))

    def context(self, symbol):
        # type: (Symbol) -> List[str]
        index_start = symbol._start_position
        index_end = symbol._end_position
        while index_start > 0:
            if self._lexdata[index_start - 1] == '\n':
                break
            index_start -= 1

        while index_end < len(self._lexdata) - 1:
            if self._lexdata[index_end + 1] == '\n':
                break
            index_end += 1
        return self._lexdata[index_start:index_end + 1].split('\n')

    def _token(self, track_blanks=False):
        # type: (bool) -> Generator[Token, None, None]
        lexpos = 0
        lexdata = self._lexdata
        lexlen = self._lexlen
        self._state_stack.append(self._states['INITIAL'])
        state = self._state_stack[-1]
        skipped_tokens = []    # type: List[Token]

        while lexpos < lexlen:
            # Look for a regular expression match
            for lexre, lexindexfunc in state._regex:
                m = lexre.match(lexdata, lexpos)
                if not m:
                    continue

                i = m.lastindex
                assert i is not None
                rule = lexindexfunc[i]
                assert rule is not None
                lexpos_end = m.end()

                tok = Token(rule[3], self, lexpos, lexpos_end, None, skipped_tokens)
                lexpos = lexpos_end

                new_token = rule[0](self, tok) # type: ignore
                state = self._state_stack[-1]
                if new_token is None:
                    if track_blanks:
                        skipped_tokens.append(tok)
                    break

                skipped_tokens = []
                yield new_token
                break
            else:
                raise SyntaxError("Illegal character '%s' at index %d" % (lexdata[lexpos], lexpos))

        tok = Token(0, self, lexpos, lexpos, None, skipped_tokens)
        self._lexpos = lexpos
        yield tok


def token(pattern, name=None, states=('INITIAL', ), warn=True):
    # type: (str, Optional[str], Tuple[str,...], bool) -> Callable[[Callable[[F, Token], Optional[Token]]], Callable[[F, Token], Optional[Token]]]
    if name is None:
        name = pattern

    def attach(method):
        # type: (Callable[[F, Token], Optional[Token]]) -> Callable[[F, Token], Optional[Token]]
        if not hasattr(method, 'patterns'):
            setattr(method, 'patterns', [(pattern, name, states, warn)])
        else:
            getattr(method, 'patterns').append((pattern, name, states, warn))
        return method

    return attach


def _form_master_re(rule_list, start_index):
    # type: (List[Tuple[str, str, Pattern[str], bool, Callable[[F, Token], Optional[Token]], str]], int) -> List[Tuple[Pattern[str], List[Optional[Tuple[Callable[[F, Token], Optional[Token]], str, bool, int]]]]]
    if not rule_list:
        return []

    regex = '|'.join('(%s)' % (rule[0]) for rule in rule_list)
    try:
        lexre = re.compile(regex)
        result = [None] * (
            1 + lexre.groups
        )                      # type: List[Optional[Tuple[Callable[[F, Token], Optional[Token]], str, bool, int]]]
        index = 0
        for i, rule in enumerate(rule_list):
            result[index + 1] = (rule[4], rule[1], rule[3], start_index + i)
            index += 1 + rule[2].groups
        return [(lexre, result)]
    except Exception as e:
        m = int(len(rule_list) / 2)
        if m == 0:
            m = 1
        return _form_master_re(rule_list[:m], start_index) + _form_master_re(rule_list[m:], start_index + m)


def _build_states(owner):
    # type: (Type[Lexer]) -> Dict[str, Lexer.State]
    rules = {}                                                                                # type: Dict[str, List[Tuple[str, str, Pattern[str], bool, Callable[[F, Token], Optional[Token]], str]]]
    for action in dir(owner):
        for rule, name, states, warn in sorted(
            getattr(getattr(owner, action), 'patterns', []), key=lambda x: x[0], reverse=True
        ):
            regex = re.compile(rule)
            for state in states:
                try:
                    rules[state].append((rule, name, regex, warn, getattr(owner, action), action))
                except KeyError:
                    rules[state] = [(rule, name, regex, warn, getattr(owner, action), action)]
    result = {}
    index = 4
    for state, rule_list in rules.items():
        result[state] = Lexer.State(_form_master_re(sorted(rule_list, key=lambda x: x[5], reverse=True), index))
        index += len(rule_list)
    return result


if TYPE_CHECKING:
    from typing import Callable, Dict, Generator, List, Optional, Pattern, Tuple, Type