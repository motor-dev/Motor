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
from ......ast.expressions import UnaryExpression, SizeofExpression, SizeofTypeExpression, SizeofPackExpression, AlignofExpression, AmbiguousExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('unary-expression : [no-merge-warning]postfix-expression')
@cxx98
def unary_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('unary-expression : unary-operator cast-expression')
@cxx98
def unary_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return UnaryExpression(p[1], p[0])


@glrp.rule('unary-expression : "++" cast-expression')
@glrp.rule('unary-expression : "--" cast-expression')
@cxx98
def unary_expression_2(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return UnaryExpression(p[1], p[0].text())


@glrp.rule('unary-expression : sizeof-expression')
@glrp.rule('unary-expression : new-expression')
@glrp.rule('unary-expression : delete-expression')
@cxx98
def unary_expression_3(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('unary-expression : "sizeof" "..." "(" identifier ")"')
@cxx11
def unary_expression_sizeof_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SizeofPackExpression(p[3].value)


@glrp.rule('unary-expression : "alignof" "(" type-id ")"')
@cxx11
def unary_expression_alignof_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AlignofExpression(p[2])


@glrp.rule('unary-expression : noexcept-expression')
@cxx11
def unary_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('unary-expression : await-expression')
@cxx20
def unary_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('sizeof-expression : "sizeof" unary-expression')
@cxx98
def sizeof_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SizeofExpression(p[1])


@glrp.rule('sizeof-expression : "sizeof" "(" begin-type-id type-id ")"')
@cxx98
def sizeof_expression_type(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SizeofTypeExpression(p[3])


@glrp.rule('unary-operator : "*" | "&" | "+" | "-" | "!" | "~"[prec:right,2]')
@cxx98
def unary_operator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0].text()


@glrp.merge('sizeof-expression')
@cxx98_merge
def ambiguous_sizeof_expression(self, type_id, ambiguous_primary_expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    expression_list = type_id + ambiguous_primary_expression
    return AmbiguousExpression(expression_list)


if TYPE_CHECKING:
    from typing import Any, List
    from .....parser import CxxParser
