"""
id-expression:
    unqualified-id
    qualified-id
"""

import glrp
from .....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('id-expression : unqualified-id')
@glrp.rule('id-expression : qualified-id')
@cxx98
def id_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('id-expression')
@cxx98
def generic_id_expression(self, template_name, generic_type_name):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    # template_name corresponds to an unqualified-id
    # generic-type-name to a qualified-id
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser