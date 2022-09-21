"""
logical-or-expression:
    logical-and-expression
    logical-or-expression || logical-and-expression
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('logical-or-expression : logical-and-expression')
@glrp.rule('logical-or-expression : logical-or-expression "||" logical-and-expression')
@cxx98
def logical_or_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser