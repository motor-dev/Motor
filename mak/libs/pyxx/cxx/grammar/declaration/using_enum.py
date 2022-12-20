"""
using-enum-declaration:
    using elaborated-enum-specifier ;
"""

import glrp
from ...parse import cxx20
from ....ast.declarations import UsingEnumDeclaration
from motor_typing import TYPE_CHECKING


# TODO: attribute-specifier-seq not allowed
@glrp.rule('using-enum-declaration : attribute-specifier-seq? begin-declaration "using" elaborated-enum-specifier ";"')
@cxx20
def using_enum_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return UsingEnumDeclaration(p[0], p[3])


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser