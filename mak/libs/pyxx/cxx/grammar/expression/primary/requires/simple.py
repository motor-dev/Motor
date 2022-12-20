"""
simple-requirement:
    expression ;
"""

import glrp
from .....parse import cxx20
from ......ast.constraints import SimpleRequirement
from motor_typing import TYPE_CHECKING


@glrp.rule('simple-requirement : expression ";"')
@cxx20
def simple_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleRequirement(p[0])


if TYPE_CHECKING:
    from typing import Any
    from .....parse import CxxParser
