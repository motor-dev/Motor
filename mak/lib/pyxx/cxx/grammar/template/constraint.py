"""
constraint-expression:
    logical-or-expression
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx20


@glrp.rule('constraint-expression : constant-expression')
@cxx20
def constraint_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]
