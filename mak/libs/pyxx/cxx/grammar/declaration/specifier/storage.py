"""
storage-class-specifier:
    static
    thread_local
    extern
    mutable
"""

import glrp
from ....parser import cxx98, cxx11, deprecated_cxx11, deprecated_cxx17
from motor_typing import TYPE_CHECKING


@glrp.rule('storage-class-specifier : "static"')
@glrp.rule('storage-class-specifier : "extern"')
@glrp.rule('storage-class-specifier : "mutable"')
@glrp.rule('storage-class-specifier : "storage-class-specifier-macro"')
@cxx98
def storage_class_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('storage-class-specifier : "thread_local"')
@cxx11
def storage_class_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('storage-class-specifier : "auto"')
@cxx98
@deprecated_cxx11
def storage_class_specifier_until_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('storage-class-specifier : "register"')
@cxx98
@deprecated_cxx17
def storage_class_specifier_until_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser