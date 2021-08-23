"""
private-module-fragment:
    module-keyword : private ; declaration-seq?
"""

import glrp
from ...parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('private-module-fragment : "module" ":" "private" ";" declaration-seq?')
@cxx20
def private_module_fragment_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser