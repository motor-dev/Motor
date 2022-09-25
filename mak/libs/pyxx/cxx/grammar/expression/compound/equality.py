"""
equality-expression:
    relational-expression
    equality-expression == relational-expression
    equality-expression != relational-expression
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('equality-expression : [no-merge-warning] relational-expression')
@glrp.rule('equality-expression : equality-expression "==" [no-merge-warning] relational-expression')
@glrp.rule('equality-expression : equality-expression "!=" [no-merge-warning] relational-expression')
@cxx98
def equality_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser