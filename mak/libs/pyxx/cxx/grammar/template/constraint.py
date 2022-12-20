"""
constraint-expression:
    logical-or-expression
"""

import glrp
from ...parse import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('constraint-expression : constraint-logical-or-expression')
@cxx20
def constraint_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


if TYPE_CHECKING:
    from typing import Any, List
    from ...parse import CxxParser