"""
constant-expression:
    conditional-expression
"""

import glrp
from ...parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('constant-expression : conditional-expression')
@cxx98
def constant_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('constant-expression? : constant-expression')
@glrp.rule('constant-expression? :')
@cxx98
def constant_expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser