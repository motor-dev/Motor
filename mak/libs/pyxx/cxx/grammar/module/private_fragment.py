"""
private-module-fragment:
    module-keyword : private ; declaration-seq?
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx20
from ....ast.module import PrivateModuleFragment
from motor_typing import TYPE_CHECKING


@glrp.rule('private-module-fragment? : "module" ":" "private" ";" declaration-seq?')
@cxx20
def private_module_fragment_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return PrivateModuleFragment(p[4])


@glrp.rule('private-module-fragment? : ')
@cxx20
def private_module_fragment_opt_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return None
