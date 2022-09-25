"""
relational-expression:
    compare-expression
    relational-expression < compare-expression
    relational-expression > compare-expression
    relational-expression <= compare-expression
    relational-expression >= compare-expression
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('relational-expression : compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression "<" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression ">" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression "<=" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression ">=" compare-expression')
@cxx98
def relational_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser