"""
decltype-specifier:
    decltype ( expression )
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx98, cxx11
from ......ast.type import DecltypeTypeSpecifier, ErrorTypeSpecifier


@glrp.rule('decltype-specifier : "decltype-macro" "(" expression ")"')
@cxx98
def decltype_specifier(self: CxxParser, p: glrp.Production) -> Any:
    position = (p[0].position[0], p[3].position[1])
    return DecltypeTypeSpecifier(position, p[0].text(), p[2])


@glrp.rule('decltype-specifier : "decltype-macro" "(" "#error" ")"')
@cxx98
def decltype_specifier_error(self: CxxParser, p: glrp.Production) -> Any:
    position = (p[0].position[0], p[3].position[1])
    return ErrorTypeSpecifier(position)


@glrp.rule('decltype-specifier : "decltype" "(" expression ")"')
@cxx11
def decltype_specifier_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    position = (p[0].position[0], p[3].position[1])
    return DecltypeTypeSpecifier(position, p[0].text(), p[2])


@glrp.rule('decltype-specifier : "decltype" "(" "#error" ")"')
@cxx11
def decltype_specifier_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    position = (p[0].position[0], p[3].position[1])
    return ErrorTypeSpecifier(position)
