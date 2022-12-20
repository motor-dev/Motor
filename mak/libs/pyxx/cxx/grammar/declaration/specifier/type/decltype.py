"""
decltype-specifier:
    decltype ( expression )
"""

import glrp
from .....parse import cxx11
from ......ast.type import DecltypeTypeSpecifier
from motor_typing import TYPE_CHECKING


@glrp.rule('decltype-specifier : "decltype" "(" expression ")"')
@glrp.rule('decltype-specifier : "decltype-macro" "(" expression ")"')
@cxx11
def decltype_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DecltypeTypeSpecifier(p[0].text(), p[2])


if TYPE_CHECKING:
    from typing import Any
    from .....parse import CxxParser