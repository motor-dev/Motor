"""
asm-declaration:
    attribute-specifier-seq? asm ( string-literal ) ;
"""

import glrp
from ...parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('asm-declaration : begin-decl-other attribute-specifier-seq? "asm" "(" "string-literal" ")" ";"')
@cxx98
def asm_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser