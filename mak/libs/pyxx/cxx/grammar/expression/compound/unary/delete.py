"""
delete-expression:
    ::? delete cast-expression
    ::? delete [ ] cast-expression
"""

import glrp
from .....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('delete-expression : "delete" cast-expression')
@glrp.rule('delete-expression : "delete" "[" [prec:left,1]"]" cast-expression')
@glrp.rule('delete-expression : "::" "delete" cast-expression')
@glrp.rule('delete-expression : "::" "delete" "[" [prec:left,1]"]" cast-expression')
@cxx98
def delete_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser