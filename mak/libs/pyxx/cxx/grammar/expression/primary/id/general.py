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
def id_expression_rename(self, unqualified_id, template_id, template_name, ambiguous_nested_name_specifier):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from motor_typing import Optional
    from .....parser import CxxParser