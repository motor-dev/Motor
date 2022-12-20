"""
module-import-declaration:
    import-keyword module-name attribute-specifier-seq? ;
    import-keyword module-partition attribute-specifier-seq? ;
    import-keyword header-name attribute-specifier-seq ;
"""

import glrp
from ...parse import cxx20
from ....ast.module import ModuleImportDeclaration
from motor_typing import TYPE_CHECKING


@glrp.rule('module-import-declaration : "import" module-name attribute-specifier-seq? ";"')
@glrp.rule('module-import-declaration : "import" module-partition attribute-specifier-seq? ";"')
#@glrp.rule('module-import-declaration : "import" header-name attribute-specifier-seq ";"')
@cxx20
def module_import_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ModuleImportDeclaration(p[1], p[2])


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser