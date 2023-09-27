from .token import Token
from ..symbol import Symbol
import re
from typing import TypeVar, Callable, Dict, Generator, List, Optional, Pattern, Tuple, Type

F = TypeVar('F', bound='Lexer')


class Lexer:
    tokens = tuple()  # type: Tuple[str,...]

    class State:

        def __init__(
                self,
                regex_list: List[Tuple[Pattern[str], List[Optional[Tuple[Callable[[F, Token], Optional[Token]], str,
                bool, int]]]]]
        ) -> None:
            self._regex = regex_list

    def __init__(self) -> None:
        self._states = {}  # type: Dict[str, Lexer.State]
        self._state_stack = []  # type: List[Lexer.State]
        self._filename = ''
        self._lexdata = ''
        self._lexlen = 0
        self._states, self._terminals = _build_states(self.__class__)
        for token_name in self.tokens:
            if token_name not in self._terminals:
                self._terminals[token_name] = (len(self._terminals), True)

    def input(self, filename: str, track_blanks: bool) -> Generator[Token, None, None]:
        self._filename = filename
        with open(filename, 'r') as file:
            self._lexdata = file.read()
            self._lexlen = len(self._lexdata)
        return self._token(track_blanks)

    def get_token_id(self, token_type: str) -> int:
        return self._terminals[token_type][0]

    def set_token_type(self, token: Token, type: str) -> Token:
        token._id = self.get_token_id(type)
        return token

    def push_state(self, state: str) -> None:
        self._state_stack.append(self._states[state])

    def pop_state(self) -> None:
        self._state_stack.pop(-1)

    def text(self, symbol: Symbol) -> str:
        return self._lexdata[symbol.position[0]:symbol.position[1]]

    def text_position(self, position: Tuple[int, int]) -> Tuple[str, Tuple[int, int], Tuple[int, int]]:
        lexdata = self._lexdata
        start_lineno = lexdata.count('\n', 0, position[0]) + 1
        line_count = lexdata.count('\n', position[0], position[1])
        end_lineno = start_lineno + line_count

        if start_lineno:
            start_column = position[0] - lexdata.rfind('\n', 0, position[0])
        else:
            start_column = position[0]

        if line_count:
            end_column = position[1] - lexdata.rfind('\n', position[0], position[1])
        else:
            end_column = start_column + position[1] - position[0]

        return self._filename, (start_lineno, start_column), (end_lineno, end_column)

    def context(self, position: Tuple[int, int]) -> List[str]:
        index_start, index_end = position
        while index_start > 0:
            if self._lexdata[index_start - 1] == '\n':
                break
            index_start -= 1

        while index_end < len(self._lexdata):
            if self._lexdata[index_end] == '\n':
                break
            index_end += 1
        return self._lexdata[index_start:index_end].split('\n')

    def _token(self, track_blanks: bool = False) -> Generator[Token, None, None]:
        lexpos = 0
        lexdata = self._lexdata
        lexlen = self._lexlen
        self._state_stack.append(self._states['INITIAL'])
        state = self._state_stack[-1]
        skipped_tokens = []  # type: List[Token]

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

                tok = Token(rule[3], self, (lexpos, lexpos_end), None, skipped_tokens)
                lexpos = lexpos_end

                new_token = rule[0](self, tok)  # type: ignore
                state = self._state_stack[-1]
                if new_token is None:
                    if track_blanks:
                        skipped_tokens.append(tok)
                    break

                skipped_tokens = []
                yield new_token
                break
            else:
                self.syntax_error(lexpos)

        tok = Token(0, self, (lexpos, lexpos), None, skipped_tokens)
        self._lexpos = lexpos
        yield tok

    def syntax_error(self, lex_position: int) -> None:
        raise SyntaxError("Illegal character '%s' at index %d" % (self._lexdata[lex_position], lex_position))


def token(
        pattern: str,
        name: Optional[str] = None,
        states: Tuple[str, ...] = ('INITIAL',),
        warn: bool = True
) -> Callable[[Callable[[F, Token], Optional[Token]]], Callable[[F, Token], Optional[Token]]]:
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


def _form_master_re(
        rule_list: List[Tuple[str, str, Pattern[str], bool, Callable[[F, Token], Optional[Token]], str]],
        terminals: Dict[str, Tuple[int, bool]]
) -> List[Tuple[Pattern[str], List[Optional[Tuple[Callable[[F, Token], Optional[Token]], str, bool, int]]]]]:
    if not rule_list:
        return []

    regex = '|'.join('(%s)' % (rule[0]) for rule in rule_list)
    try:
        lexre = re.compile(regex)
        result = [None] * (
                1 + lexre.groups
        )  # type: List[Optional[Tuple[Callable[[F, Token], Optional[Token]], str, bool, int]]]
        index = 0
        for rule in rule_list:
            try:
                terminal_index, _ = terminals[rule[1]]
            except KeyError:
                terminal_index = len(terminals)
                terminals[rule[1]] = (terminal_index, rule[3])
            result[index + 1] = (rule[4], rule[1], rule[3], terminal_index)
            index += 1 + rule[2].groups
        return [(lexre, result)]
    except Exception as e:
        m = int(len(rule_list) / 2)
        if m == 0:
            m = 1
        return _form_master_re(rule_list[:m], start_index) + _form_master_re(rule_list[m:], start_index + m)


def _build_states(owner: Type[Lexer]) -> Tuple[Dict[str, Lexer.State], Dict[str, Tuple[int, bool]]]:
    rules = {}  # type: Dict[str, List[Tuple[str, str, Pattern[str], bool, Callable[[F, Token], Optional[Token]], str]]]
    terminals = {'#eof': (0, False), '#mark': (1, False), '#start': (2, False), '#error': (3, False)}

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
    indices = []  # type: List[str]
    for state, rule_list in rules.items():
        result[state] = Lexer.State(
            _form_master_re(sorted(rule_list, key=lambda x: x[5], reverse=True), terminals))

    return result, terminals
