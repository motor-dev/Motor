"""
expression:
    assignment-expression
    expression , assignment-expression
"""

import glrp
from ....parse import cxx98
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('expression : expression-proxy')
@glrp.rule('expression? : expression')
@cxx98
def expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('expression-proxy : assignment-expression')
@cxx98
def expression_proxy_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('expression-proxy : expression-proxy "," assignment-expression')
@cxx98
def expression_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('expression? : ')
@cxx98
def expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser