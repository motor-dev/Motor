import glrp
from . import lexer
from ..messages import Logger
from typing import Any, Callable, cast


class CParser(glrp.Parser):
    Lexer = lexer.C89Lexer

    def __init__(self, logger: Logger, tmp_dir: str, mode: int = glrp.LOAD_CACHE) -> None:
        self.lexer = self.__class__.Lexer()
        glrp.Parser.__init__(self, self.lexer, 'translation-unit', tmp_dir, mode)


class C89Parser(CParser):
    Lexer = lexer.C89Lexer


class C99Parser(C89Parser):
    Lexer = lexer.C99Lexer


class C11Parser(C99Parser):
    Lexer = lexer.C11Lexer


class C17Parser(C11Parser):
    Lexer = lexer.C17Lexer


class C23Parser(C17Parser):
    Lexer = lexer.C23Lexer


def c89(func: Callable[[CParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(C89Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def c99(func: Callable[[CParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(C99Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def c11(func: Callable[[CParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(C11Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


def c17(func: Callable[[CParser, glrp.Production], Any]) -> Callable[[glrp.Parser, glrp.Production], Any]:
    setattr(C17Parser, func.__name__, func)
    return cast(Callable[[glrp.Parser, glrp.Production], Any], func)


from . import grammar
