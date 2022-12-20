"""
global-module-fragment:
    module-keyword ; declaration-seq?
"""

import glrp
from ...parse import cxx20
from ....ast.module import GlobalModuleFragment
from motor_typing import TYPE_CHECKING


@glrp.rule('global-module-fragment : "module" ";" [prec:right,1]')
@cxx20
def global_module_fragment_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return GlobalModuleFragment([])


@glrp.rule('global-module-fragment : "module" ";" declaration-seq')
@cxx20
def global_module_fragment_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return GlobalModuleFragment(p[2])


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser