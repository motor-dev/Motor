"""
delete-expression:
    ::? delete cast-expression
    ::? delete [ ] cast-expression
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx98
from ......ast.expressions import DeleteExpression


@glrp.rule('delete-expression : "delete" cast-expression')
@cxx98
def delete_expression(self: CxxParser, p: glrp.Production) -> Any:
    return DeleteExpression(p[1], False, False)


@glrp.rule('delete-expression : "delete" "[" [prec:left,1]"]" cast-expression')
@cxx98
def delete_expression_array(self: CxxParser, p: glrp.Production) -> Any:
    return DeleteExpression(p[3], True, False)


@glrp.rule('delete-expression : "::" "delete" cast-expression')
@cxx98
def delete_expression_root(self: CxxParser, p: glrp.Production) -> Any:
    return DeleteExpression(p[2], False, True)


@glrp.rule('delete-expression : "::" "delete" "[" [prec:left,1]"]" cast-expression')
@cxx98
def delete_expression_root_array(self: CxxParser, p: glrp.Production) -> Any:
    return DeleteExpression(p[4], True, True)