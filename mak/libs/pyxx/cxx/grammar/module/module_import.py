"""
module-import-declaration:
    import-keyword module-name attribute-specifier-seq? ;
    import-keyword module-partition attribute-specifier-seq? ;
    import-keyword header-name attribute-specifier-seq ;
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx20
from ....ast.module import ModuleImportDeclaration


@glrp.rule('module-import-declaration : "import" module-name attribute-specifier-seq? ";"')
@glrp.rule('module-import-declaration : "import" module-partition attribute-specifier-seq? ";"')
#@glrp.rule('module-import-declaration : "import" header-name attribute-specifier-seq ";"')
@cxx20
def module_import_declaration_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ModuleImportDeclaration(p[1], p[2])
