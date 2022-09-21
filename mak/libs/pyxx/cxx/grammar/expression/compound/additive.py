"""
additive-expression:
    multiplicative-expression
    additive-expression + multiplicative-expression
    additive-expression - multiplicative-expression
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('additive-expression : multiplicative-expression')
@glrp.rule('additive-expression : additive-expression "+" multiplicative-expression')
@glrp.rule('additive-expression : additive-expression "-" multiplicative-expression')
@cxx98
def additive_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser