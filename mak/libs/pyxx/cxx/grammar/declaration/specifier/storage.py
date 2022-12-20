"""
storage-class-specifier:
    static
    thread_local
    extern
    mutable
"""

import glrp
from ....parse import cxx98, cxx11, deprecated_cxx11, deprecated_cxx17
from .....ast.declarations import StorageClassSpecifiers, StorageClassSpecifierMacro
from motor_typing import TYPE_CHECKING


@glrp.rule('storage-class-specifier : "static"')
@cxx98
def storage_class_specifier_static(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StorageClassSpecifiers.STATIC


@glrp.rule('storage-class-specifier : "extern"')
@cxx98
def storage_class_specifier_extern(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StorageClassSpecifiers.EXTERN


@glrp.rule('storage-class-specifier : "mutable"')
@cxx98
def storage_class_specifier_mutable(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StorageClassSpecifiers.MUTABLE


@glrp.rule('storage-class-specifier : "storage-class-specifier-macro"')
@cxx98
def storage_class_specifier_macro(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StorageClassSpecifierMacro(p[0], None)


@glrp.rule('storage-class-specifier : "storage-class-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def storage_class_specifier_macro_function(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StorageClassSpecifierMacro(p[0], p[2])


@glrp.rule('storage-class-specifier : "thread_local"')
@cxx11
def storage_class_specifier_thread_local_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StorageClassSpecifiers.THREAD_LOCAL


@glrp.rule('storage-class-specifier : "auto"')
@cxx98
@deprecated_cxx11
def storage_class_specifier_auto_until_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StorageClassSpecifiers.AUTO


@glrp.rule('storage-class-specifier : "register"')
@cxx98
@deprecated_cxx17
def storage_class_specifier_register_until_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StorageClassSpecifiers.REGISTER


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser