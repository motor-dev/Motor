"""
await-expression:
    co_await cast-expression
"""

import glrp
from .....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('await-expression : "co_await" cast-expression')
@cxx98
def await_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser