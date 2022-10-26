"""
delete-expression:
    ::? delete cast-expression
    ::? delete [ ] cast-expression
"""

import glrp
from .....parser import cxx98
from ......ast.expressions import DeleteExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('delete-expression : "delete" cast-expression')
@cxx98
def delete_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DeleteExpression(p[1], False, False)


@glrp.rule('delete-expression : "delete" "[" [prec:left,1]"]" cast-expression')
@cxx98
def delete_expression_array(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DeleteExpression(p[3], True, False)


@glrp.rule('delete-expression : "::" "delete" cast-expression')
@cxx98
def delete_expression_root(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DeleteExpression(p[2], False, True)


@glrp.rule('delete-expression : "::" "delete" "[" [prec:left,1]"]" cast-expression')
@cxx98
def delete_expression_root_array(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DeleteExpression(p[4], True, True)


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser