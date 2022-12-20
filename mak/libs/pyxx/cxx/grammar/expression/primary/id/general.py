"""
id-expression:
    unqualified-id
    qualified-id
"""

import glrp
from .....parse import cxx98
from ......ast.reference import Reference
from motor_typing import TYPE_CHECKING


@glrp.rule('id-expression : unqualified-id')
@cxx98
def id_expression_unqualified(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference([(False, p[0])])


@glrp.rule('id-expression : qualified-id')
@cxx98
def id_expression_qualified(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference(p[0])


if TYPE_CHECKING:
    from typing import Any, List
    from .....parse import CxxParser