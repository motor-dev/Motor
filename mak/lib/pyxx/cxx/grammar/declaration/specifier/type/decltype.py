"""
decltype-specifier:
    decltype ( expression )
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx11
from ......ast.type import DecltypeTypeSpecifier, ErrorTypeSpecifier


@glrp.rule('decltype-specifier : "decltype" "(" expression ")"')
@glrp.rule('decltype-specifier : "decltype-macro" "(" expression ")"')
@cxx11
def decltype_specifier_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return DecltypeTypeSpecifier(p[0].text(), p[2])


@glrp.rule('decltype-specifier : "decltype" "(" "#error" ")"')
@glrp.rule('decltype-specifier : "decltype-macro" "(" "#error" ")"')
@cxx11
def decltype_specifier_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorTypeSpecifier()
