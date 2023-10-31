"""
export-declaration:
    export declaration
    export { declaration-seq? }
    export-keyword module-import-declaration
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx20
from ....ast.module import ExportDeclaration


@glrp.rule('export-declaration : [prec:right,1]"export" declaration')
@glrp.rule('export-declaration[prec:right,1] : [prec:right,1]"export" module-import-declaration')
@cxx20
def export_declaration_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ExportDeclaration([p[1]])


@glrp.rule('export-declaration : [prec:right,1]"export" "{" declaration-seq? "}"')
@cxx20
def export_declaration_seq_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ExportDeclaration(p[2])
