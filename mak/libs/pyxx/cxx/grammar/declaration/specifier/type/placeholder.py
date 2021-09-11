"""
placeholder-type-specifier:
    type-constraint? auto
    type-constraint? decltype ( auto )
"""

import glrp
from .....parser import cxx11, cxx14, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('placeholder-type-specifier : [prec:left,1]"auto"')
@cxx11
def placeholder_type_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('placeholder-type-specifier : [split]"decltype" "(" "auto" ")"')
@cxx14
def placeholder_type_specifier_cxx14(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('placeholder-type-specifier : type-constraint "auto"')
@glrp.rule('placeholder-type-specifier : type-constraint "decltype" "(" "auto" ")"')
@cxx20
def placeholder_type_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser