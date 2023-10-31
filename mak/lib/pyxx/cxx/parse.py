import glrp
from . import lex
from ..messages import Logger
from typing import Callable, cast, Any


class CxxParser(glrp.Parser):
    Lexer = lex.Cxx98Lexer

    def __init__(self, logger: Logger, tmp_dir: str, mode: int = glrp.LOAD_CACHE) -> None:
        self.logger = logger
        self.lexer = self.__class__.Lexer(logger)
        if self.logger:
            self.logger.set_lexer(self.lexer)
        glrp.Parser.__init__(self, self.lexer, 'translation-unit', tmp_dir, mode)


class Cxx98Parser(CxxParser):
    Lexer = lex.Cxx98Lexer


class Cxx03Parser(Cxx98Parser):
    Lexer = lex.Cxx03Lexer


class Cxx11Parser(Cxx03Parser):
    Lexer = lex.Cxx11Lexer


class Cxx14Parser(Cxx11Parser):
    Lexer = lex.Cxx14Lexer


class Cxx17Parser(Cxx14Parser):
    Lexer = lex.Cxx17Lexer


class Cxx20Parser(Cxx17Parser):
    Lexer = lex.Cxx20Lexer


class Cxx23Parser(Cxx20Parser):
    Lexer = lex.Cxx23Lexer


def _empty_rule(parser: glrp.Parser, production: glrp.Production) -> Any:
    pass


def cxx98_merge(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(Cxx98Parser, func.__name__, func)
    return func


def cxx98(func: Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx98Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx03_merge(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(Cxx03Parser, func.__name__, func)
    return func


def cxx03(func: Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx03Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx11_merge(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(Cxx11Parser, func.__name__, func)
    return func


def cxx11(func: Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx11Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx14_merge(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(Cxx14Parser, func.__name__, func)
    return func


def cxx14(func: Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx14Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx17_merge(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(Cxx17Parser, func.__name__, func)
    return func


def cxx17(func: Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx17Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx20_merge(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(Cxx20Parser, func.__name__, func)
    return func


def cxx20(func: Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx20Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def cxx23_merge(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(Cxx23Parser, func.__name__, func)
    return func


def cxx23(func: Callable[[CxxParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx23Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx03(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(Cxx03Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx11(
        func: Callable[[CxxParser, glrp.Production], Any]
) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx11Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx14(
        func: Callable[[CxxParser, glrp.Production], Any]
) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx14Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx17(
        func: Callable[[CxxParser, glrp.Production], Any]
) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx17Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx20(
        func: Callable[[CxxParser, glrp.Production], Any]
) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx20Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def deprecated_cxx23(
        func: Callable[[CxxParser, glrp.Production], Any]
) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(Cxx23Parser, func.__name__, _empty_rule)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


from . import grammar
