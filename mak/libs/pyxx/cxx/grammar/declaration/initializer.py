"""
initializer:
    brace-or-equal-initializer
    ( expression-list )

brace-or-equal-initializer:
    = initializer-clause
    braced-init-list

initializer-clause:
    assignment-expression
    braced-init-list

braced-init-list:
    { initializer-list ,? }
    { designated-initializer-list ,? }
    { }

initializer-list:
    initializer-clause ...?
    initializer-list , initializer-clause ...?

designated-initializer-list:
    designated-initializer-clause
    designated-initializer-list , designated-initializer-clause

designated-initializer-clause:
    designator brace-or-equal-initializer

designator:
    . identifier

expr-or-braced-init-list:
    expression
    braced-init-list
"""

import glrp
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx11, cxx20, cxx98_merge
from ....ast.expressions import AmbiguousExpression, ParenthesizedExpression, ErrorExpression
from ....ast.literals import BracedInitList, AmbiguousBracedInitList, DesignatedBracedInitList, DesignatedInitializer
from ....ast.pack import PackExpandExpression


@glrp.rule('initializer : brace-or-equal-initializer')
@cxx98
def initializer(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('initializer : "(" expression-list ")"')
@cxx98
def initializer_expr_list(self: CxxParser, p: glrp.Production) -> Any:
    return ParenthesizedExpression(p[1])


@glrp.rule('initializer : "(" "#error" ")"')
@cxx98
def initializer_expr_list_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('brace-or-equal-initializer : "=" initializer-clause')
@cxx98
def brace_or_equal_initializer(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('brace-or-equal-initializer : braced-init-list')
@cxx11
def brace_or_equal_initializer_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('initializer-clause : assignment-expression')
@glrp.rule('initializer-clause : braced-init-list')
@glrp.rule('"initializer-clause#" : "assignment-expression#"')
@glrp.rule('"initializer-clause#" : braced-init-list')
@cxx98
def initializer_clause(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('braced-init-list : "{" initializer-list ","? "}"')
@cxx98
def braced_init_list(self: CxxParser, p: glrp.Production) -> Any:
    if len(p[1]) == 1:
        return BracedInitList(p[1][0])
    else:
        return AmbiguousBracedInitList([BracedInitList(init_list) for init_list in sorted(p[1], key=lambda x: len(x))])


@glrp.rule('braced-init-list : "{"  "}"')
@cxx98
def braced_init_list_empty(self: CxxParser, p: glrp.Production) -> Any:
    return BracedInitList([])


@glrp.rule('braced-init-list : "{" "#error" "}"')
@cxx98
def braced_init_list_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('braced-init-list : "{" designated-initializer-list ","? "}"')
@cxx20
def braced_init_list_designated_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return DesignatedBracedInitList(p[1])


@glrp.rule('initializer-list : initializer-clause "..."?')
@cxx98
def initializer_list_last(self: CxxParser, p: glrp.Production) -> Any:
    if p[1]:
        return [[PackExpandExpression(p[0])]]
    else:
        return [[p[0]]]


@glrp.rule('initializer-list : initializer-list "," initializer-clause "..."?')
@cxx98
def initializer_list(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    expr = p[2]
    if p[3]:
        expr = PackExpandExpression(p[3])
    for l in result:
        l.append(expr)
    return result


@glrp.rule('designated-initializer-list : designated-initializer-clause')
@cxx20
def designated_initializer_list_last_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]]


@glrp.rule('designated-initializer-list : designated-initializer-list "," designated-initializer-clause')
@cxx20
def designated_initializer_list_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(p[2])
    return result


@glrp.rule('designated-initializer-clause : designator brace-or-equal-initializer')
@cxx20
def designated_initializer_clause_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return DesignatedInitializer(p[0], p[1])


@glrp.rule('designator : "." "identifier"')
@cxx20
def designator_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[1].value


@glrp.rule('expr-or-braced-init-list : expression')
@glrp.rule('expr-or-braced-init-list? : expression')
@cxx98
def expr_or_braced_init_list(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('expr-or-braced-init-list : braced-init-list')
@glrp.rule('expr-or-braced-init-list? : braced-init-list')
@cxx11
def expr_or_braced_init_list_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('expr-or-braced-init-list? : ')
@cxx98
def expr_or_braced_init_list_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('","? : ","')
@glrp.rule('","? : ')
@cxx98
def comma_opt(self: CxxParser, p: glrp.Production) -> Any:
    pass


@glrp.merge('initializer-clause')
@cxx98_merge
def ambiguous_initializer_clause(self: CxxParser, ambiguous_expression: List[Any]) -> Any:
    return AmbiguousExpression(ambiguous_expression)


@glrp.merge('initializer-clause#')
@glrp.merge_result('ambiguous_initializer_clause')
@cxx98_merge
def ambiguous_initializer_clause_ext(self: CxxParser, ambiguous_expression: List[Any]) -> Any:
    return AmbiguousExpression(ambiguous_expression)


@glrp.merge('initializer-list')
@cxx98_merge
def ambiguous_initializer_list(
    self: CxxParser, ambiguous_initializer_list: List[Any], ambiguous_initializer_clause: List[Any]
) -> Any:
    return sum(ambiguous_initializer_list + ambiguous_initializer_clause, [])
