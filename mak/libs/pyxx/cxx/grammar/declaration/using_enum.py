"""
using-enum-declaration:
    using elaborated-enum-specifier ;
"""

import glrp
from ...parser import cxx20
from motor_typing import TYPE_CHECKING


# TODO: attribute-specifier-seq not allowed
@glrp.rule('using-enum-declaration : begin-decl-other attribute-specifier-seq? "using" elaborated-enum-specifier ";"')
@cxx20
def using_enum_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser