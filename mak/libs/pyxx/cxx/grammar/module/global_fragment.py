"""
global-module-fragment:
    module-keyword ; declaration-seq?
"""

import glrp
from ...parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('global-module-fragment : "module" ";" [prec:right,1]')
@glrp.rule('global-module-fragment : "module" ";" declaration-seq')
@cxx20
def global_module_fragment_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser