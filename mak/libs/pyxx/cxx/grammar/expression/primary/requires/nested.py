"""
nested-requirement:
    requires constraint-expression ;
"""

import glrp
from .....parse import cxx20
from ......ast.constraints import NestedRequirement
from motor_typing import TYPE_CHECKING


@glrp.rule('nested-requirement : [prec:left,1]"requires" constraint-expression ";"')
@cxx20
def nested_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NestedRequirement(p[1])


if TYPE_CHECKING:
    from typing import Any
    from .....parse import CxxParser
