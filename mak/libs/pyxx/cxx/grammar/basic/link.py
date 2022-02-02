"""
translation-unit:
    declaration-seq?
    global-module-fragment? module-declaration declaration-seq? private-module-fragment?
"""

import glrp
from ...parser import cxx98, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('translation-unit : declaration-seq?')
@cxx98
def translation_unit(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


#@glrp.rule('translation-unit : module-declaration declaration-seq? private-module-fragment?')
#@glrp.rule('translation-unit : global-module-fragment module-declaration declaration-seq? private-module-fragment?')
#@cxx20
#def translation_unit_cxx20(self, p):
#    # type: (CxxParser, glrp.Production) -> None
#    pass

if TYPE_CHECKING:
    from ...parser import CxxParser