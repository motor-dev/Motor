"""
id-expression:
    unqualified-id
    qualified-id
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx98
from ......ast.reference import Reference
from motor_typing import TYPE_CHECKING


@glrp.rule('id-expression : unqualified-id')
@cxx98
def id_expression_unqualified(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([p[0]])


@glrp.rule('id-expression : qualified-id')
@cxx98
def id_expression_qualified(self: CxxParser, p: glrp.Production) -> Any:
    return Reference(p[0])
