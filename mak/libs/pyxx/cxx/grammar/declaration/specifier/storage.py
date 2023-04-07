"""
storage-class-specifier:
    static
    thread_local
    extern
    mutable
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx11, deprecated_cxx11, deprecated_cxx17
from .....ast.declarations import StorageClassSpecifiers, StorageClassSpecifierMacro


@glrp.rule('storage-class-specifier : "static"')
@cxx98
def storage_class_specifier_static(self: CxxParser, p: glrp.Production) -> Any:
    return StorageClassSpecifiers.STATIC


@glrp.rule('storage-class-specifier : "extern"')
@cxx98
def storage_class_specifier_extern(self: CxxParser, p: glrp.Production) -> Any:
    return StorageClassSpecifiers.EXTERN


@glrp.rule('storage-class-specifier : "mutable"')
@cxx98
def storage_class_specifier_mutable(self: CxxParser, p: glrp.Production) -> Any:
    return StorageClassSpecifiers.MUTABLE


@glrp.rule('storage-class-specifier : "storage-class-specifier-macro"')
@cxx98
def storage_class_specifier_macro(self: CxxParser, p: glrp.Production) -> Any:
    return StorageClassSpecifierMacro(p[0], None)


@glrp.rule('storage-class-specifier : "storage-class-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def storage_class_specifier_macro_function(self: CxxParser, p: glrp.Production) -> Any:
    return StorageClassSpecifierMacro(p[0], p[2])


@glrp.rule('storage-class-specifier : "thread_local"')
@cxx11
def storage_class_specifier_thread_local_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return StorageClassSpecifiers.THREAD_LOCAL


@glrp.rule('storage-class-specifier : "auto"')
@cxx98
@deprecated_cxx11
def storage_class_specifier_auto_until_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return StorageClassSpecifiers.AUTO


@glrp.rule('storage-class-specifier : "register"')
@cxx98
@deprecated_cxx17
def storage_class_specifier_register_until_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return StorageClassSpecifiers.REGISTER
