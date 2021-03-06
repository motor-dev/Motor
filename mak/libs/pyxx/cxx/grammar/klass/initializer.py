"""
ctor-initializer:
    : mem-initializer-list

mem-initializer-list:
    mem-initializer ...?
    mem-initializer-list , mem-initializer ...?

mem-initializer:
    mem-initializer-id ( expression-list? )
    mem-initializer-id braced-init-list

mem-initializer-id:
    class-or-decltype
    identifier
"""

import glrp
from ...parser import cxx98, cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('ctor-initializer : ":" mem-initializer-list')
@cxx98
def ctor_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('ctor-initializer? : ":" mem-initializer-list')
@glrp.rule('ctor-initializer? : ')
@cxx98
def ctor_initializer_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('mem-initializer-list : mem-initializer')
@glrp.rule('mem-initializer-list : mem-initializer-list "," mem-initializer')
@cxx98
def mem_initializer_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('mem-initializer-list : mem-initializer "..."')
@glrp.rule('mem-initializer-list : mem-initializer-list "," mem-initializer "..."')
@cxx11
def mem_initializer_list_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('mem-initializer : mem-initializer-id "(" expression-list? ")"')
@cxx98
def mem_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('mem-initializer : mem-initializer-id braced-init-list')
@cxx11
def mem_initializer_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('mem-initializer-id : class-or-decltype')
@glrp.rule('mem-initializer-id : "identifier"')
@cxx98
def mem_initializer_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser