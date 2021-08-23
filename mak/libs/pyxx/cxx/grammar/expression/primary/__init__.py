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
from ....parser import cxx98, cxx11, cxx17, cxx20
from motor_typing import TYPE_CHECKING
from . import id
from . import lambda_expr
from . import fold
from . import requires


@glrp.rule('primary-expression[split] : "integer-literal"')
@glrp.rule('primary-expression : "character-literal"')
@glrp.rule('primary-expression : "floating-literal"')
@glrp.rule('primary-expression : "string-literal"')
@glrp.rule('primary-expression : "this"')
@glrp.rule('primary-expression : "true"')
@glrp.rule('primary-expression : "false"')
@glrp.rule('primary-expression : [split]"(" expression ")"')
@glrp.rule('primary-expression[split] : id-expression')
@cxx98
def primary_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('primary-expression : "user-defined-integer-literal"')
@glrp.rule('primary-expression : "user-defined-character-literal"')
@glrp.rule('primary-expression : "user-defined-floating-literal"')
@glrp.rule('primary-expression : "user-defined-string-literal"')
@glrp.rule('primary-expression : lambda-expression')
@cxx11
def primary_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('primary-expression : fold-expression')
@cxx17
def primary_expression_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('primary-expression : requires-expression')
@cxx20
def primary_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser