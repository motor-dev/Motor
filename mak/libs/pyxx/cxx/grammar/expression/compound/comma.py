"""
expression:
    assignment-expression
    expression , assignment-expression
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('expression : assignment-expression')
@glrp.rule('expression : expression "," assignment-expression')
@cxx98
def expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('expression? : expression')
@glrp.rule('expression? : ')
@cxx98
def expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser