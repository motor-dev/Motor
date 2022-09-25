"""
id-expression:
    unqualified-id
    qualified-id
"""

import glrp
from .....parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('id-expression : unqualified-id')
@glrp.rule('id-expression : qualified-id')
@cxx98
def id_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from .....parser import CxxParser