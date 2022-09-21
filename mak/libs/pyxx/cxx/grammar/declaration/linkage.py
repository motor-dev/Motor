"""
linkage-specification:
    extern string-literal { declaration-seq? }
    extern string-literal declaration
"""

import glrp
from ...parser import cxx98
from motor_typing import TYPE_CHECKING


# TODO: attribute-specifier-seq? not allowed
@glrp.rule(
    'linkage-specification : begin-decl-other attribute-specifier-seq? "extern" "string-literal" "{" declaration-seq? "}"'
)
@glrp.rule('linkage-specification : begin-decl-other attribute-specifier-seq? "extern" "string-literal" declaration')
@cxx98
def linkage_specification(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser