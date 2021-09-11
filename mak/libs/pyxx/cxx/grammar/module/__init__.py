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
from ...parser import cxx20
from motor_typing import TYPE_CHECKING
from . import module_export
from . import module_import
from . import global_fragment
from . import private_fragment


@glrp.rule('module-declaration : "module" module-name module-partition? attribute-specifier-seq? ";"')
@glrp.rule('module-declaration : "export" "module" module-name module-partition? attribute-specifier-seq? ";"')
@cxx20
def module_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('module-name : module-name-qualifier? "identifier"')
@cxx20
def module_name_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('module-partition : ":" module-name-qualifier? "identifier"')
@cxx20
def module_partition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('module-partition? : ":" module-name-qualifier? "identifier"')
@glrp.rule('module-partition? : ')
@cxx20
def module_partition_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('module-name-qualifier? : module-name-qualifier? "identifier" "."')
@glrp.rule('module-name-qualifier? : ')
@cxx20
def module_name_qualifier_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser