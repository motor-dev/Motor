"""
module-import-declaration:
    import-keyword module-name attribute-specifier-seq? ;
    import-keyword module-partition attribute-specifier-seq? ;
    import-keyword header-name attribute-specifier-seq ;
"""

import glrp
from ...parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('module-import-declaration : "import" module-name attribute-specifier-seq? ";"')
@glrp.rule('module-import-declaration : "import" module-partition attribute-specifier-seq? ";"')
#@glrp.rule('module-import-declaration : "import" header-name attribute-specifier-seq ";"')
@cxx20
def module_import_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser