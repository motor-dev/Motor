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
from ...parse import cxx98, cxx11, cxx20, cxx98_merge
from ....ast.expressions import AmbiguousExpression
from ....ast.literals import BracedInitList, DesignatedBracedInitList, DesignatedInitializer
from motor_typing import TYPE_CHECKING


@glrp.rule('initializer : brace-or-equal-initializer')
@cxx98
def initializer(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('initializer : "(" expression-list ")"')
@cxx98
def initializer_expr_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule('brace-or-equal-initializer : "=" initializer-clause')
@cxx98
def brace_or_equal_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule('brace-or-equal-initializer : braced-init-list')
@cxx11
def brace_or_equal_initializer_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('initializer-clause : assignment-expression')
@glrp.rule('initializer-clause : braced-init-list')
@glrp.rule('"initializer-clause#" : "assignment-expression#"')
@glrp.rule('"initializer-clause#" : braced-init-list')
@cxx98
def initializer_clause(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('braced-init-list : "{" initializer-list ","? "}"')
@cxx98
def braced_init_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BracedInitList(p[1])


@glrp.rule('braced-init-list : "{"  "}"')
@cxx98
def braced_init_list_empty(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BracedInitList([[]])


@glrp.rule('braced-init-list : "{" designated-initializer-list ","? "}"')
@cxx20
def braced_init_list_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DesignatedBracedInitList(p[1])


@glrp.rule('initializer-list : initializer-clause "..."?')
@cxx98
def initializer_list_last(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [[(p[0], p[1])]]


@glrp.rule('initializer-list : initializer-list "," initializer-clause "..."?')
@cxx98
def initializer_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    for l in result:
        l.append((p[2], p[3]))
    return result


@glrp.rule('designated-initializer-list : designated-initializer-clause')
@cxx20
def designated_initializer_list_last_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [p[0]]


@glrp.rule('designated-initializer-list : designated-initializer-list "," designated-initializer-clause')
@cxx20
def designated_initializer_list_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append(p[2])
    return result


@glrp.rule('designated-initializer-clause : designator brace-or-equal-initializer')
@cxx20
def designated_initializer_clause_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DesignatedInitializer(p[0], p[1])


@glrp.rule('designator : "." "identifier"')
@cxx20
def designator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1].value


@glrp.rule('expr-or-braced-init-list : expression')
@glrp.rule('expr-or-braced-init-list? : expression')
@cxx98
def expr_or_braced_init_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('expr-or-braced-init-list : braced-init-list')
@glrp.rule('expr-or-braced-init-list? : braced-init-list')
@cxx11
def expr_or_braced_init_list_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('expr-or-braced-init-list? : ')
@cxx98
def expr_or_braced_init_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.rule('","? : ","')
@glrp.rule('","? : ')
@cxx98
def comma_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('initializer-clause')
@cxx98_merge
def ambiguous_initializer_clause(self, ambiguous_expression):
    # type: (CxxParser, List[Any]) -> Any
    return AmbiguousExpression(ambiguous_expression)


@glrp.merge('initializer-clause#')
@glrp.merge_result('ambiguous_initializer_clause')
@cxx98_merge
def ambiguous_initializer_clause_ext(self, ambiguous_expression):
    # type: (CxxParser, List[Any]) -> Any
    return AmbiguousExpression(ambiguous_expression)


@glrp.merge('initializer-list')
@cxx98_merge
def ambiguous_initializer_list(self, ambiguous_initializer_list, ambiguous_initializer_clause):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return sum(ambiguous_initializer_list + ambiguous_initializer_clause, [])


if TYPE_CHECKING:
    from typing import Any, List
    from ...parse import CxxParser