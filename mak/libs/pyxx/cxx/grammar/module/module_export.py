"""
export-declaration:
    export declaration
    export { declaration-seq? }
    export-keyword module-import-declaration
"""

import glrp
from ...parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('export-declaration : [prec:left,0]"export" noexport-declaration')
@glrp.rule('export-declaration : [prec:left,0]"export" "{" noexport-declaration-seq? "}"')
@glrp.rule('export-declaration : [prec:left,0]"export" module-import-declaration')
@cxx20
def export_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser