"""
compound-requirement:
    { expression } noexcept? return-type-requirement? ;
return-type-requirement:
    -> type-constraint
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx20
from ......ast.constraints import CompoundRequirement, ErrorRequirement
from ......ast.expressions import ErrorExpression


@glrp.rule('compound-requirement : "{" expression "}" "noexcept"? return-type-requirement? ";"')
@cxx20
def compound_requirement_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return CompoundRequirement(p[1], p[3], p[4])


@glrp.rule('compound-requirement : "{" "#error" "}" "noexcept"? return-type-requirement? ";"')
@cxx20
def compound_requirement_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return CompoundRequirement(ErrorExpression(), p[3], p[4])


@glrp.rule('compound-requirement : "{" expression "}" "#error" ";"')
@glrp.rule('compound-requirement : "{" "#error" "}" "#error" ";"')
@cxx20
def compound_requirement_error_2_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorRequirement()


@glrp.rule('"noexcept"? : "noexcept"')
@cxx20
def noexcept_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return True


@glrp.rule('"noexcept"? : ')
@cxx20
def noexcept_opt_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return False


@glrp.rule('return-type-requirement? : "->" type-constraint')
@cxx20
def return_type_requirement_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('return-type-requirement? : ')
@cxx20
def return_type_requirement_opt_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return None
