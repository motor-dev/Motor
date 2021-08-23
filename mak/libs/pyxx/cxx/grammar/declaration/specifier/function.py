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
@glrp.rule('function-specifier[split] : explicit-specifier')
@cxx98
def function_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('explicit-specifier : "explicit"[split]')
@cxx98
def explicit_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('explicit-specifier : "explicit"[split] "(" constant-expression ")"')
@cxx20
def explicit_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser