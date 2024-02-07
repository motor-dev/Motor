"""
constant-expression:
    conditional-expression
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx98


@glrp.rule('constant-expression? : constant-expression')
@cxx98
def constant_expression(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('constant-expression? :')
@cxx98
def constant_expression_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None
