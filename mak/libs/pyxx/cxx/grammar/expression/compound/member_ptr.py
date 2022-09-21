"""
pm-expression:
    cast-expression
    pm-expression .* cast-expression
    pm-expression ->* cast-expression
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('pm-expression : cast-expression')
@glrp.rule('pm-expression : pm-expression ".*" cast-expression')
@glrp.rule('pm-expression : pm-expression "->*" cast-expression')
@cxx98
def pm_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser