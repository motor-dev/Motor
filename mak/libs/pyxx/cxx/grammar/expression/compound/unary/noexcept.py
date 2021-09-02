"""
noexcept-expression:
    noexcept ( expression )
"""

import glrp
from .....parser import cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('noexcept-expression : "noexcept" "(" expression ")"')
@cxx11
def noexcept_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser