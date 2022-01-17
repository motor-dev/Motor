"""
decltype-specifier:
    decltype ( expression )
"""

import glrp
from .....parser import cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('decltype-specifier : "decltype" "(" expression ")"')
@cxx11
def decltype_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser