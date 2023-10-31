"""
using-enum-declaration:
    using elaborated-enum-specifier ;
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx20
from ....ast.declarations import UsingEnumDeclaration


# TODO: attribute-specifier-seq not allowed
@glrp.rule('using-enum-declaration : attribute-specifier-seq? begin-declaration "using" elaborated-enum-specifier ";"')
@cxx20
def using_enum_declaration_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return UsingEnumDeclaration(p[0], p[3])
