"""
function-specifier:
    virtual
    explicit-specifier

explicit-specifier:
    explicit ( constant-expression )
    explicit
"""

import glrp
from ....parser import cxx98, cxx20
from .....ast.declarations import ExplicitSpecifier, FunctionSpecifiers
from motor_typing import TYPE_CHECKING


@glrp.rule('function-specifier : "virtual"')
@cxx98
def function_specifier_virtual(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return FunctionSpecifiers.VIRTUAL


@glrp.rule('function-specifier : explicit-specifier')
@cxx98
def function_specifier_explicit(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('explicit-specifier : "explicit"')
@cxx98
def explicit_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ExplicitSpecifier(None)


@glrp.rule('explicit-specifier : "explicit" [prec:left,1]"(" constant-expression ")"')
@cxx20
def explicit_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ExplicitSpecifier(p[2])


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser