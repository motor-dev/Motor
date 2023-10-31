"""
asm-declaration:
    attribute-specifier-seq? asm ( string-literal ) ;
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx98
from ....ast.declarations import AsmDeclaration, ErrorDeclaration
from typing import TYPE_CHECKING


@glrp.rule('asm-declaration : attribute-specifier-seq? begin-declaration "asm" "(" "string-literal" ")" ";"')
@cxx98
def asm_declaration(self: CxxParser, p: glrp.Production) -> Any:
    return AsmDeclaration(p[0], p[4].value)


@glrp.rule('asm-declaration : attribute-specifier-seq? begin-declaration "asm" "(" "#error" ")" ";"')
@cxx98
def asm_declaration_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorDeclaration()
