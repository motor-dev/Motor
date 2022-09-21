"""
exception-specification:
    (until c++17)
    dynamic-exception-specification
    noexcept-specification

dynamic-exception-specification:
    (until c++17)
    throw ( type-id-list )
    (until c++20)
    throw ( )

type-id-list:
    type-id ...opt
    type-id-list , type-id ...opt

noexcept-specification:
    (since c++11)
    noexcept ( constant-expression )
    noexcept
"""

import glrp
from ...parser import cxx98, cxx11, deprecated_cxx17, deprecated_cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('exception-specification? : ')
@cxx98
def exception_specification_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('exception-specification? : dynamic-exception-specification')
@cxx98
@deprecated_cxx20
def exception_specification_opt_until_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('exception-specification? : noexcept-specification')
@cxx11
def exception_specification_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('dynamic-exception-specification : "throw" "(" type-id-list ")"')
@cxx98
@deprecated_cxx17
def dynamic_exception_specification_until_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('dynamic-exception-specification : "throw" "(" ")"')
@cxx98
@deprecated_cxx20
def dynamic_exception_specification_until_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('type-id-list : type-id "..."?')
@glrp.rule('type-id-list : type-id-list "," type-id "..."?')
@cxx98
@deprecated_cxx17
def type_id_list_until_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('noexcept-specification : "noexcept"  [prec:left,1]"(" constant-expression ")"')
@glrp.rule('noexcept-specification : "noexcept" ')
@cxx11
def noexcept_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('noexcept-specification? : noexcept-specification')
@glrp.rule('noexcept-specification? :')
@cxx11
def noexcept_specifier_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser