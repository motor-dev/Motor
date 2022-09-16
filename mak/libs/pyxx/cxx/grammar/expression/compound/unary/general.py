"""
unary-expression:
    postfix-expression
    unary-operator cast-expression
    ++ cast-expression
    -- cast-expression
    await-expression
    sizeof unary-expression
    sizeof ( type-id )
    sizeof ... ( identifier )
    alignof ( type-id )
    noexcept-expression
    new-expression
    delete-expression

unary-operator: one of
    *  &  +  -  !  ~
"""

import glrp
from .....parser import cxx98, cxx11, cxx20, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('unary-expression : postfix-expression')
@glrp.rule('unary-expression : unary-operator cast-expression')
@glrp.rule('unary-expression : "++" cast-expression')
@glrp.rule('unary-expression : "--" cast-expression')
@glrp.rule('unary-expression : sizeof-expression')
@glrp.rule('unary-expression : new-expression')
@glrp.rule('unary-expression : delete-expression')
@cxx98
def unary_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('unary-expression : "sizeof" "..." "(" identifier ")"')
@glrp.rule('unary-expression : "alignof" "(" type-id ")"')
@glrp.rule('unary-expression : noexcept-expression')
@cxx11
def unary_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('unary-expression : await-expression')
@cxx20
def unary_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('sizeof-expression : "sizeof" unary-expression')
@glrp.rule('sizeof-expression : "sizeof" "(" begin-type-id type-id ")"')
@cxx98
def sizeof_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('unary-operator : "*" | "&" | "+" | "-" | "!" | "~"[prec:right,2]')
@cxx98
def unary_operator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('sizeof-expression')
@cxx98_merge
def ambiguous_sizeof_expression(self, type_id, ambiguous_primary_expression):
    # type: (CxxParser, Any, Any) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser
