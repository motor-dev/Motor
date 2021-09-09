"""
equality-expression:
    relational-expression
    equality-expression == relational-expression
    equality-expression != relational-expression
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('equality-expression : relational-expression[split]')
@glrp.rule('equality-expression : equality-expression "==" relational-expression[split]')
@glrp.rule('equality-expression : equality-expression "!=" relational-expression[split]')
@cxx98
def equality_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser