from .production import Production
from .grammar import Grammar
from .context import Context
from ..lex import Token
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


class _OptionalAction(Action):
    def __init__(self, action, optional_index):
        # type: (Action, int) -> None
        Action.__init__(self)
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
        rules = self._grammar._rules

        for token in self._lexer.token():
            for context in contexts:
                action = action_table[context._state_stack[-1]].get(token._id, None)
                if len(actions) == 0:
                    pass   # TODO
                else:
                    for action in actions:
                        actions
                        if action < 0:
                            rule = rules[-action]
                            action_list.append()
                        else:
                            action_list.append((context, action))

            if t is not None:
                if t > 0:
                    # shift a symbol on the stack
                    statestack.append(t)
                    state = t

                    symstack.append(lookahead)
                    lookahead = None

                    # Decrease error count on successful shift
                    if errorcount:
                        errorcount -= 1
                    continue

                if t < 0:
                    # reduce a symbol on the stack, emit a production
                    p = prod[-t]
                    pname = p.name
                    plen = p.len

                    # Get production function
                    sym = YaccSymbol()
                    sym.type = pname   # Production name
                    sym.value = None

                    if plen:
                        targ = symstack[-plen - 1:]
                        targ[0] = sym

                        #--! TRACKING
                        if tracking:
                            t1 = targ[1]
                            sym.lineno = t1.lineno
                            sym.lexpos = t1.lexpos
                            t1 = targ[-1]
                            sym.endlineno = getattr(t1, 'endlineno', t1.lineno)
                            sym.endlexpos = getattr(t1, 'endlexpos', t1.lexpos)
                        #--! TRACKING

                        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # The code enclosed in this section is duplicated
                        # below as a performance optimization.  Make sure
                        # changes get made in both locations.

                        pslice.slice = targ

                        try:
                            # Call the grammar rule with our special slice object
                            del symstack[-plen:]
                            self.state = state
                            p.callable(pslice)
                            del statestack[-plen:]
                            symstack.append(sym)
                            state = goto[statestack[-1]][pname]
                            statestack.append(state)
                        except SyntaxError:
                            # If an error was set. Enter error recovery state
                            lookaheadstack.append(lookahead) # Save the current lookahead token
                            symstack.extend(targ[1:-1])      # Put the production slice back on the stack
                            statestack.pop()                 # Pop back one state (before the reduce)
                            state = statestack[-1]
                            sym.type = 'error'
                            sym.value = 'error'
                            lookahead = sym
                            errorcount = error_count
                            self.errorok = False

                        continue
                        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                    else:

                        #--! TRACKING
                        if tracking:
                            sym.lineno = lexer.lineno
                            sym.lexpos = lexer.lexpos
                        #--! TRACKING

                        targ = [sym]

                        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # The code enclosed in this section is duplicated
                        # above as a performance optimization.  Make sure
                        # changes get made in both locations.

                        pslice.slice = targ

                        try:
                            # Call the grammar rule with our special slice object
                            self.state = state
                            p.callable(pslice)
                            symstack.append(sym)
                            state = goto[statestack[-1]][pname]
                            statestack.append(state)
                        except SyntaxError:
                            # If an error was set. Enter error recovery state
                            lookaheadstack.append(lookahead) # Save the current lookahead token
                            statestack.pop()                 # Pop back one state (before the reduce)
                            state = statestack[-1]
                            sym.type = 'error'
                            sym.value = 'error'
                            lookahead = sym
                            errorcount = error_count
                            self.errorok = False

                        continue
                        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                if t == 0:
                    n = symstack[-1]
                    result = getattr(n, 'value', None)
                    return result

            if t is None:

                # We have some kind of parsing error here.  To handle
                # this, we are going to push the current token onto
                # the tokenstack and replace it with an 'error' token.
                # If there are any synchronization rules, they may
                # catch it.
                #
                # In addition to pushing the error token, we call call
                # the user defined p_error() function if this is the
                # first syntax error.  This function is only called if
                # errorcount == 0.
                if errorcount == 0 or self.errorok:
                    errorcount = error_count
                    self.errorok = False
                    errtoken = lookahead
                    if errtoken.type == '$end':
                        errtoken = None # End of file!
                    if self.errorfunc:
                        if errtoken and not hasattr(errtoken, 'lexer'):
                            errtoken.lexer = lexer
                        self.state = state
                        tok = call_errorfunc(self.errorfunc, errtoken, self)
                        if self.errorok:
                                        # User must have done some kind of panic
                                        # mode recovery on their own.  The
                                        # returned token is the next lookahead
                            lookahead = tok
                            errtoken = None
                            continue
                    else:
                        if errtoken:
                            if hasattr(errtoken, 'lineno'):
                                lineno = lookahead.lineno
                            else:
                                lineno = 0
                            if lineno:
                                sys.stderr.write('yacc: Syntax error at line %d, token=%s\n' % (lineno, errtoken.type))
                            else:
                                sys.stderr.write('yacc: Syntax error, token=%s' % errtoken.type)
                        else:
                            sys.stderr.write('yacc: Parse error in input. EOF\n')
                            return

                else:
                    errorcount = error_count

                # case 1:  the statestack only has 1 entry on it.  If we're in this state, the
                # entire parse has been rolled back and we're completely hosed.   The token is
                # discarded and we just keep going.

                if len(statestack) <= 1 and lookahead.type != '$end':
                    lookahead = None
                    errtoken = None
                    state = 0
                    # Nuke the pushback stack
                    del lookaheadstack[:]
                    continue

                # case 2: the statestack has a couple of entries on it, but we're
                # at the end of the file. nuke the top entry and generate an error token

                # Start nuking entries on the stack
                if lookahead.type == '$end':
                    # Whoa. We're really hosed here. Bail out
                    return

                if lookahead.type != 'error':
                    sym = symstack[-1]
                    if sym.type == 'error':
                        # Hmmm. Error is on top of stack, we'll just nuke input
                        # symbol and continue
                        #--! TRACKING
                        if tracking:
                            sym.endlineno = getattr(lookahead, 'lineno', sym.lineno)
                            sym.endlexpos = getattr(lookahead, 'lexpos', sym.lexpos)
                        #--! TRACKING
                        lookahead = None
                        continue

                    # Create the error symbol for the first time and make it the new lookahead symbol
                    t = YaccSymbol()
                    t.type = 'error'

                    if hasattr(lookahead, 'lineno'):
                        t.lineno = t.endlineno = lookahead.lineno
                    if hasattr(lookahead, 'lexpos'):
                        t.lexpos = t.endlexpos = lookahead.lexpos
                    t.value = lookahead
                    lookaheadstack.append(lookahead)
                    lookahead = t
                else:
                    sym = symstack.pop()
                    #--! TRACKING
                    if tracking:
                        lookahead.lineno = sym.lineno
                        lookahead.lexpos = sym.lexpos
                    #--! TRACKING
                    statestack.pop()
                    state = statestack[-1]

                continue

            # Call an error function here
            raise RuntimeError('yacc: internal parser error!!!\n')

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