"""
simple-requirement:
    expression ;
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx20
from ......ast.constraints import SimpleRequirement, ErrorRequirement


@glrp.rule('simple-requirement : expression ";"')
@cxx20
def simple_requirement_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleRequirement(p[0])


@glrp.rule('simple-requirement : "#error" ";"')
@cxx20
def simple_requirement_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorRequirement()
