"""
inclusive-or-expression:
    exclusive-or-expression
    inclusive-or-expression | exclusive-or-expression
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('inclusive-or-expression : exclusive-or-expression')
@glrp.rule('inclusive-or-expression : inclusive-or-expression "|" exclusive-or-expression')
@cxx98
def inclusive_or_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser