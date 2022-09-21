"""
primary-expression:
    literal
    this
    ( expression )
    id-expression
    lambda-expression
    fold-expression
    requires-expression
"""

import glrp
from ....parser import cxx98, cxx11, cxx17, cxx20, cxx98_merge
from motor_typing import TYPE_CHECKING
from . import id
from . import lambda_expr
from . import fold
from . import requires


@glrp.rule('primary-expression : "integer-literal"[split:initializer]')
@glrp.rule('primary-expression : "character-literal"')
@glrp.rule('primary-expression : "floating-literal"')
@glrp.rule('primary-expression : "string-literal"')
@glrp.rule('primary-expression : "this"')
@glrp.rule('primary-expression : "true"')
@glrp.rule('primary-expression : "false"')
@glrp.rule('primary-expression : primary-expression-proxy')
@glrp.rule('primary-expression[prec:right,1] : id-expression')
@cxx98
def primary_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('primary-expression-proxy : "(" begin-expression expression ")"')
@cxx98
def primary_expression_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('primary-expression : "user-defined-integer-literal"')
@glrp.rule('primary-expression : "user-defined-character-literal"')
@glrp.rule('primary-expression : "user-defined-floating-literal"')
@glrp.rule('primary-expression : "user-defined-string-literal"')
@glrp.rule('primary-expression : lambda-expression')
@cxx11
def primary_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('primary-expression-proxy : fold-expression')
@cxx17
def primary_expression_proxy_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('primary-expression : requires-expression')
@cxx20
def primary_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('primary-expression-proxy')
@cxx98_merge
def ambiguous_primary_expression(self, expression, fold_expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser