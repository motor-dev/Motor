import glrp
from . import lexer
from .. import tables
import os
from motor_typing import Callable, TYPE_CHECKING, cast, Any


class CxxParser(glrp.Parser):
    Lexer = glrp.Lexer

    class TokenFilter(glrp.Context.TokenCallback):

        def __init__(self, lexer):
            # type: (glrp.Lexer) -> None
            glrp.Context.TokenCallback.__init__(self)
            self._nested_count = 0
            self._lexer = lexer
            self._opening_ids = (lexer.get_token_id('['), lexer.get_token_id('('), lexer.get_token_id('{'))
            self._closing_ids = (lexer.get_token_id(']'), lexer.get_token_id(')'), lexer.get_token_id('}'))
            self._closing_bracket = lexer.get_token_id('>')

        def filter(self, context, token):
            # type: (glrp.Context, glrp.Token) -> List[glrp.Token]
            if token._id in self._opening_ids:
                self._nested_count += 1
            elif token._id in self._closing_ids:
                self._nested_count -= 1
            elif self._nested_count == 0 and token._id == self._closing_bracket:
                token = token.duplicate()
                self._lexer.set_token_type(token, '%>')
                context._filters.pop(-1)
            return [token]

        def clone(self):
            # type: () -> glrp.Context.TokenCallback
            result = CxxParser.TokenFilter(self._lexer)
            result._nested_count = self._nested_count
            return result

    def __init__(self, tmp_dir, mode=glrp.LOAD_CACHE):
        # type: (str, int)->None
        self.lexer = self.__class__.Lexer()
        out_dir = os.path.dirname(tables.__file__)
        glrp.Parser.__init__(self, self.lexer, 'translation-unit', tmp_dir, out_dir, mode)

    def begin_template_list(self, context):
        # type: (glrp.Context) -> None
        context._filters.append(CxxParser.TokenFilter(self.lexer))


class Cxx98Parser(CxxParser):
    Lexer = lexer.Cxx98Lexer


class Cxx03Parser(Cxx98Parser):
    Lexer = lexer.Cxx03Lexer


class Cxx11Parser(Cxx03Parser):
    Lexer = lexer.Cxx11Lexer

    class TokenFilter(glrp.Context.TokenCallback):

        def __init__(self, lexer):
            # type: (glrp.Lexer) -> None
            glrp.Context.TokenCallback.__init__(self)
            self._nested_count = 0
            self._lexer = lexer
            self._opening_ids = (lexer.get_token_id('['), lexer.get_token_id('('), lexer.get_token_id('{'))
            self._opening_ids_double = (lexer.get_token_id('[['), )
            self._closing_ids = (lexer.get_token_id(']'), lexer.get_token_id(')'), lexer.get_token_id('}'))
            self._closing_bracket = lexer.get_token_id('>')
            self._closing_bracket_double = lexer.get_token_id('>>')

        def filter(self, context, token):
            # type: (glrp.Context, glrp.Token) -> List[glrp.Token]
            if token._id in self._opening_ids:
                self._nested_count += 1
            elif token._id in self._opening_ids_double:
                self._nested_count += 2
            elif token._id in self._closing_ids:
                self._nested_count -= 1
            elif self._nested_count == 0 and token._id == self._closing_bracket:
                token = token.duplicate()
                self._lexer.set_token_type(token, '%>')
                context._filters.pop(-1)
            elif self._nested_count == 0 and token._id == self._closing_bracket_double:
                token = token.duplicate()
                token2 = token.duplicate()
                self._lexer.set_token_type(token, '%>')
                self._lexer.set_token_type(token2, '>')
                context._filters.pop(-1)
                return [token] + context._filters[-1].filter(context, token2)
            return [token]

        def clone(self):
            # type: () -> glrp.Context.TokenCallback
            result = Cxx11Parser.TokenFilter(self._lexer)
            result._nested_count = self._nested_count
            return result

    def begin_template_list(self, context):
        # type: (glrp.Context) -> None
        context._filters.append(Cxx11Parser.TokenFilter(self.lexer))


class Cxx14Parser(Cxx11Parser):
    Lexer = lexer.Cxx14Lexer


class Cxx17Parser(Cxx14Parser):
    Lexer = lexer.Cxx17Lexer


class Cxx20Parser(Cxx17Parser):
    Lexer = lexer.Cxx20Lexer


class Cxx23Parser(Cxx20Parser):
    Lexer = lexer.Cxx23Lexer


def _empty_rule(parser, production):
    # type: (glrp.Parser, glrp.Production) -> Any
    pass


def cxx98_merge(func):
    # type: (Callable[..., Any]) -> Callable[..., Any]
    setattr(Cxx98Parser, func.__name__, func)
    return func


def cxx98(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx98Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx03_merge(func):
    # type: (Callable[..., Any]) -> Callable[..., Any]
    setattr(Cxx03Parser, func.__name__, func)
    return func


def cxx03(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx03Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx11_merge(func):
    # type: (Callable[..., Any]) -> Callable[..., Any]
    setattr(Cxx11Parser, func.__name__, func)
    return func


def cxx11(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx11Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx14_merge(func):
    # type: (Callable[..., Any]) -> Callable[..., Any]
    setattr(Cxx14Parser, func.__name__, func)
    return func


def cxx14(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx14Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx17_merge(func):
    # type: (Callable[..., Any]) -> Callable[..., Any]
    setattr(Cxx17Parser, func.__name__, func)
    return func


def cxx17(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx17Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx20_merge(func):
    # type: (Callable[..., Any]) -> Callable[..., Any]
    setattr(Cxx20Parser, func.__name__, func)
    return func


def cxx20(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx20Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx23_merge(func):
    # type: (Callable[..., Any]) -> Callable[..., Any]
    setattr(Cxx23Parser, func.__name__, func)
    return func


def cxx23(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx23Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx03(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx03Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx11(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx11Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx14(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx14Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx17(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx17Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx20(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx20Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx23(func):
    # type: (Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]
    setattr(Cxx23Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


from . import grammar
if TYPE_CHECKING:
    from motor_typing import Any, List