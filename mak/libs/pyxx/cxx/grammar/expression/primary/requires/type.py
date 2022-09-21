"""
type-requirement:
    typename nested-name-specifier? type-name ;
"""

import glrp
from .....parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('type-requirement : type-name ";"')
# TODO: template not allowed
@glrp.rule('type-requirement : nested-name-specifier template? type-name ";"')
@cxx20
def type_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser
