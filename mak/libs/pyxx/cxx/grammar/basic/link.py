"""
translation-unit:
    declaration-seq?
    global-module-fragment? module-declaration declaration-seq? private-module-fragment?
"""

import glrp
from ...parse import cxx98, cxx20
from ....ast.translation_unit import TranslationUnit
from motor_typing import TYPE_CHECKING


@glrp.rule('translation-unit : declaration-seq?')
@cxx98
def translation_unit(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TranslationUnit(None, None, p[0], [])


@glrp.rule('translation-unit : module-declaration declaration-seq? private-module-fragment?')
@cxx20
def translation_unit_module_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TranslationUnit(None, p[0], p[1], p[2])


@glrp.rule('translation-unit : global-module-fragment module-declaration declaration-seq? private-module-fragment?')
@cxx20
def translation_unit_global_module_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TranslationUnit(p[0], p[1], p[2], p[3])


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser