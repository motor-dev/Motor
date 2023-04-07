"""
expression:
    assignment-expression
    expression , assignment-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('expression : expression-proxy')
@glrp.rule('expression? : expression')
@cxx98
def expression(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('expression-proxy : assignment-expression')
@cxx98
def expression_proxy_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('expression-proxy : expression-proxy "," assignment-expression')
@cxx98
def expression_proxy(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('expression? : ')
@cxx98
def expression_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None