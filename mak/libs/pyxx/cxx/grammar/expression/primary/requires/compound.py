"""
compound-requirement:
    { expression } noexcept? return-type-requirement? ;
return-type-requirement:
    -> type-constraint
"""

import glrp
from .....parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('compound-requirement : "{" expression "}" "noexcept"? return-type-requirement? ";"')
@cxx20
def compound_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('"noexcept"? : "noexcept"')
@glrp.rule('"noexcept"? : ')
@cxx20
def noexcept_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('return-type-requirement? : "->" type-constraint')
@glrp.rule('return-type-requirement? : ')
@cxx20
def return_type_requirement_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser
