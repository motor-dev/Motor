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
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('id-expression')
@glrp.merge_result('id_expression')
@cxx98_merge
def id_expression_rename(self, nested_name_specifier, unqualified_id):
    # type: (CxxParser, Any, Any) -> None
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser