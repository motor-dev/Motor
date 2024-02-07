"""
delete-expression:
    ::? delete cast-expression
    ::? delete [ ] cast-expression
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx98, cxx20
from ......ast.expressions import DeleteExpression


@glrp.rule('constant-expression[prec:right,15] : [prec:right,15]"delete" constant-expression')
@glrp.rule('constant-expression#[prec:right,15] : [prec:right,15]"delete" constant-expression#')
@cxx98
def delete_expression(self: CxxParser, p: glrp.Production) -> Any:
    return DeleteExpression(p[1], False, False)


@glrp.rule('constant-expression[prec:right,15] : [prec:right,15]"delete" "[" [prec:left,1]"]" constant-expression')
@glrp.rule('constant-expression#[prec:right,15] : [prec:right,15]"delete" "[" [prec:left,1]"]" constant-expression#')
@cxx98
def delete_expression_array(self: CxxParser, p: glrp.Production) -> Any:
    return DeleteExpression(p[3], True, False)


@glrp.rule('constant-expression[prec:right,15] : [prec:right,15]"::" "delete" constant-expression')
@glrp.rule('constant-expression#[prec:right,15] : [prec:right,15]"::" "delete" constant-expression#')
@cxx98
def delete_expression_root(self: CxxParser, p: glrp.Production) -> Any:
    return DeleteExpression(p[2], False, True)


@glrp.rule('constant-expression[prec:right,15] : [prec:right,15]"::" "delete" "[" [prec:left,1]"]" constant-expression')
@glrp.rule(
    'constant-expression#[prec:right,15] : [prec:right,15]"::" "delete" "[" [prec:left,1]"]" constant-expression#')
@cxx98
def delete_expression_root_array(self: CxxParser, p: glrp.Production) -> Any:
    return DeleteExpression(p[4], True, True)
