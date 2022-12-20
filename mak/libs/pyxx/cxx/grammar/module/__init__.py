"""
module-declaration:
    export-keyword? module-keyword module-name module-partition? attribute-specifier-seq? ;

module-name:
    module-name-qualifier? identifier

module-partition:
    : module-name-qualifier? identifier

module-name-qualifier:
    identifier .
    module-name-qualifier identifier .
"""

import glrp
from ...parse import cxx20
from ....ast.module import ModuleDeclaration
from motor_typing import TYPE_CHECKING
from . import module_export
from . import module_import
from . import global_fragment
from . import private_fragment


@glrp.rule('module-declaration : "module" module-name module-partition? attribute-specifier-seq? ";"')
@cxx20
def module_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ModuleDeclaration(p[1], p[2], p[3], False)


@glrp.rule('module-declaration : "export" "module" module-name module-partition? attribute-specifier-seq? ";"')
@cxx20
def module_declaration_export_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ModuleDeclaration(p[2], p[3], p[4], True)


@glrp.rule('module-name : module-name-qualifier? "identifier"')
@glrp.rule('module-name-qualifier? : module-name-qualifier? "identifier" "."')
@cxx20
def module_name_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0] + [p[1].text()]


@glrp.rule('module-partition : ":" module-name-qualifier? "identifier"')
@glrp.rule('module-partition? : ":" module-name-qualifier? "identifier"')
@cxx20
def module_partition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1] + [p[2].text()]


@glrp.rule('module-partition? : ')
@cxx20
def module_partition_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.rule('module-name-qualifier? : ')
@cxx20
def module_name_qualifier_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return []


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser