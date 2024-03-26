"""
using-enum-declaration:
    using elaborated-enum-specifier ;
"""

import glrp
from typing import Any, Dict, Tuple
from ...parse import CxxParser, cxx20
from ....ast.declarations import UsingEnumDeclaration
from ....messages import error, Logger


@error
def invalid_attribute_using_enum_declaration(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an attribute cannot appear before a using enum declaration"""
    return locals()


@glrp.rule('using-enum-declaration : attribute-specifier-seq? begin-declaration "using" elaborated-enum-specifier ";"')
@cxx20
def using_enum_declaration_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    if p[0]:
        invalid_attribute_using_enum_declaration(self.logger, p[0][0].position)
    return UsingEnumDeclaration(p[3])
