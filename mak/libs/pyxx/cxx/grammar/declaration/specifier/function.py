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
from motor_typing import TYPE_CHECKING


@glrp.rule('function-specifier : "virtual"')
@glrp.rule('function-specifier : explicit-specifier')
@cxx98
def function_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('explicit-specifier : "explicit"')
@cxx98
def explicit_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('explicit-specifier : "explicit" [prec:left,1]"(" constant-expression ")"')
@cxx20
def explicit_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser