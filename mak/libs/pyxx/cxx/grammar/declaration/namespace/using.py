"""
using-directive:
    attribute-specifier-seq? using namespace nested-name-specifier? namespace-name ;
"""

import glrp
from ....parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('using-directive : begin-decl-other attribute-specifier-seq? "using" "namespace" namespace-name ";"')
@glrp.rule(
    'using-directive : begin-decl-other attribute-specifier-seq? "using" "namespace" nested-name-specifier template? namespace-name ";"'
)
@cxx98
def using_directive(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser