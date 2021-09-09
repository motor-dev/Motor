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
from ...parser import cxx98, cxx11, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('initializer : brace-or-equal-initializer')
@glrp.rule('initializer : "(" expression-list ")"')
@cxx98
def initializer(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('initializer? : brace-or-equal-initializer')
@glrp.rule('initializer? : "(" expression-list ")"')
@glrp.rule('initializer? : ')
@cxx98
def initializer_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('brace-or-equal-initializer : "=" initializer-clause')
@cxx98
def brace_or_equal_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('brace-or-equal-initializer : braced-init-list')
@cxx11
def brace_or_equal_initializer_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('brace-or-equal-initializer? : "=" initializer-clause')
@glrp.rule('brace-or-equal-initializer? : ')
@cxx98
def brace_or_equal_initializer_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('brace-or-equal-initializer? : braced-init-list')
@cxx11
def brace_or_equal_initializer_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('initializer-clause : assignment-expression')
@glrp.rule('initializer-clause : braced-init-list')
@cxx98
def initializer_clause(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('braced-init-list : "{" initializer-list ","? "}"')
@glrp.rule('braced-init-list : "{"  "}"')
@cxx98
def braced_init_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('braced-init-list : "{" designated-initializer-list ","? "}"')
@cxx20
def braced_init_list_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('initializer-list : initializer-clause "..."?')
@glrp.rule('initializer-list : initializer-list "," initializer-clause "..."?')
@cxx98
def initializer_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('designated-initializer-list : designated-initializer-clause')
@glrp.rule('designated-initializer-list : designated-initializer-list "," designated-initializer-clause')
@cxx20
def designated_initializer_list_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('designated-initializer-clause : designator brace-or-equal-initializer')
@cxx20
def designated_initializer_clause_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('designator : "." "identifier"')
@cxx20
def designator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('expr-or-braced-init-list : expression')
@cxx98
def expr_or_braced_init_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('expr-or-braced-init-list : braced-init-list')
@cxx11
def expr_or_braced_init_list_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('expr-or-braced-init-list? : expression')
@glrp.rule('expr-or-braced-init-list? : ')
@cxx98
def expr_or_braced_init_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('expr-or-braced-init-list? : braced-init-list')
@cxx11
def expr_or_braced_init_list_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('","? : ","')
@glrp.rule('","? : ')
@cxx98
def comma_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser