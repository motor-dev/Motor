"""
constant-expression:
    conditional-expression
"""

import glrp
from ...parse import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('constant-expression : conditional-expression')
@glrp.rule('"constant-expression#" : "conditional-expression#"')
@glrp.rule('constant-expression? : constant-expression')
@cxx98
def constant_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('constant-expression? :')
@cxx98
def constant_expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser