"""
asm-declaration:
    attribute-specifier-seq? asm ( string-literal ) ;
"""

import glrp
from ...parse import cxx98
from ....ast.declarations import AsmDeclaration
from motor_typing import TYPE_CHECKING


@glrp.rule('asm-declaration : attribute-specifier-seq? begin-declaration "asm" "(" "string-literal" ")" ";"')
@cxx98
def asm_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AsmDeclaration(p[0], p[4].value)


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser