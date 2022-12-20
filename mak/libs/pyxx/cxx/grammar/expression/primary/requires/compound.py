"""
compound-requirement:
    { expression } noexcept? return-type-requirement? ;
return-type-requirement:
    -> type-constraint
"""

import glrp
from .....parse import cxx20
from ......ast.constraints import CompoundRequirement
from motor_typing import TYPE_CHECKING


@glrp.rule('compound-requirement : "{" expression "}" "noexcept"? return-type-requirement? ";"')
@cxx20
def compound_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return CompoundRequirement(p[1], p[3], p[4])


@glrp.rule('"noexcept"? : "noexcept"')
@cxx20
def noexcept_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return True


@glrp.rule('"noexcept"? : ')
@cxx20
def noexcept_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return False


@glrp.rule('return-type-requirement? : "->" type-constraint')
@cxx20
def return_type_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule('return-type-requirement? : ')
@cxx20
def return_type_requirement_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


if TYPE_CHECKING:
    from typing import Any
    from .....parse import CxxParser
