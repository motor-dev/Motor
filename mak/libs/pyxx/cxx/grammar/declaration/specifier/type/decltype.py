"""
decltype-specifier:
    decltype ( expression )
"""

import glrp
from .....parser import cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('decltype-specifier : "decltype" "(" expression ")"')
@glrp.rule('decltype-specifier : "decltype-macro" "(" expression ")"')
@cxx11
def decltype_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser