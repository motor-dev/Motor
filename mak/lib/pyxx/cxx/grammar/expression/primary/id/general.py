"""
id-expression:
    unqualified-id
    qualified-id
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx98, cxx20
from ......ast.reference import Reference
from typing import TYPE_CHECKING


@glrp.rule('constant-expression : unqualified-id')
@glrp.rule('constant-expression# : unqualified-id')
@glrp.rule('id-expression: unqualified-id')
@cxx98
def id_expression_unqualified(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([p[0]])


@glrp.rule('constraint-logical-expression: constraint-unqualified-id')
@cxx20
def id_expression_unqualified_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([p[0]])


@glrp.rule('constant-expression : qualified-id')
@glrp.rule('constant-expression#: qualified-id')
@glrp.rule('id-expression: qualified-id')
@cxx98
def id_expression_qualified(self: CxxParser, p: glrp.Production) -> Any:
    return Reference(p[0])


@glrp.rule('constraint-logical-expression: constraint-qualified-id')
@cxx20
def id_expression_qualified_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return Reference(p[0])
