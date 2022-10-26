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
from ...parser import cxx98, cxx11, deprecated_cxx17, deprecated_cxx20, cxx98_merge
from ....ast.types import DynamicExceptionSpecifier, NoExceptSpecifier, TypeIdPack
from motor_typing import TYPE_CHECKING


@glrp.rule('exception-specification? : ')
@cxx98
def exception_specification_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.rule('exception-specification? : dynamic-exception-specification')
@cxx98
#@deprecated_cxx20
def exception_specification_opt_until_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('exception-specification? : noexcept-specification')
@cxx11
def exception_specification_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('dynamic-exception-specification : "throw" "(" type-id-list ")"')
@cxx98
#@deprecated_cxx17
def dynamic_exception_specification_until_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DynamicExceptionSpecifier(p[2])


@glrp.rule('dynamic-exception-specification : "throw" "(" ")"')
@cxx98
#@deprecated_cxx20
def dynamic_exception_specification_until_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DynamicExceptionSpecifier(None)


@glrp.rule('type-id-list : [no-merge-warning]type-id "..."?')
@cxx98
#@deprecated_cxx17
def type_id_list_end_until_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    if p[1]:
        return [TypeIdPack(p[0])]
    else:
        return [p[0]]


@glrp.rule('type-id-list : type-id-list "," [no-merge-warning]type-id "..."?')
@cxx98
#@deprecated_cxx17
def type_id_list_until_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    if p[3]:
        result.append(TypeIdPack(p[2]))
    else:
        result.append(p[2])
    return result


@glrp.rule('noexcept-specification : "noexcept"  [prec:left,1]"(" constant-expression ")"')
@cxx11
def noexcept_specifier_constant_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NoExceptSpecifier(p[2])


@glrp.rule('noexcept-specification : "noexcept" ')
@cxx11
def noexcept_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NoExceptSpecifier(None)


@glrp.rule('noexcept-specification? : noexcept-specification')
@cxx11
def noexcept_specifier_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('noexcept-specification? :')
@cxx11
def noexcept_specifier_opt_empty_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.merge('type-id-list')
@cxx98_merge
def ambiguous_type_id_list_ellipsis(self, end_declarator_list, continue_declarator_list):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import List, Any
    from ...parser import CxxParser