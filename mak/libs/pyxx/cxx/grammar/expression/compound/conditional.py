"""
conditional-expression:
    logical-or-expression
    logical-or-expression ? expression : assignment-expression
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('conditional-expression : logical-or-expression')
@glrp.rule('conditional-expression : logical-or-expression "?" expression ":" assignment-expression')
@cxx98
def conditional_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser