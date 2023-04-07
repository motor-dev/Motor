"""
nested-requirement:
    requires constraint-expression ;
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx20
from ......ast.constraints import NestedRequirement, ErrorRequirement


@glrp.rule('nested-requirement : [prec:left,1]"requires" constraint-expression ";"')
@cxx20
def nested_requirement_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return NestedRequirement(p[1])


@glrp.rule('nested-requirement : [prec:left,1]"requires" "#error" ";"')
@cxx20
def nested_requirement_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorRequirement()
