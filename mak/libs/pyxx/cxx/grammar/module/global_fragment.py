"""
global-module-fragment:
    module-keyword ; declaration-seq?
"""

import glrp
from ...parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('global-module-fragment[prec:right,1] : "module" ";"')
@glrp.rule('global-module-fragment[prec:right,1] : "module" ";" declaration-seq')
@cxx20
def global_module_fragment_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser