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
from typing import List, Any
from ...parse import CxxParser, cxx98, cxx11, cxx98_merge
from ....ast.type import DynamicExceptionSpecifier, AmbiguousExceptionSpecifier, NoExceptSpecifier, TypeIdPack, ExceptionSpecifierError


@glrp.rule('exception-specification? : ')
@cxx98
def exception_specification_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('exception-specification? : dynamic-exception-specification')
@cxx98
#@deprecated_cxx20
def exception_specification_opt_until_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('exception-specification? : noexcept-specification')
@cxx11
def exception_specification_opt_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('dynamic-exception-specification : "throw" "(" type-id-list ")"')
@cxx98
#@deprecated_cxx17
def dynamic_exception_specification_until_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    if len(p[2]) == 1:
        return DynamicExceptionSpecifier(p[2][0])
    else:
        type_list = sorted(p[2], key=lambda x: len(x))
        return AmbiguousExceptionSpecifier([DynamicExceptionSpecifier(t) for t in type_list])


@glrp.rule('dynamic-exception-specification : "throw" "(" "#error" ")"')
@cxx98
#@deprecated_cxx17
def dynamic_exception_specification_error_until_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return ExceptionSpecifierError()


@glrp.rule('dynamic-exception-specification : "throw" "(" ")"')
@cxx98
#@deprecated_cxx20
def dynamic_exception_specification_until_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return DynamicExceptionSpecifier([])


@glrp.rule('type-id-list : [no-merge-warning]type-id "..."?')
@cxx98
#@deprecated_cxx17
def type_id_list_end_until_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    if p[1]:
        return [[TypeIdPack(p[0])]]
    else:
        return [[p[0]]]


@glrp.rule('type-id-list : type-id-list "," [no-merge-warning]type-id "..."?')
@cxx98
#@deprecated_cxx17
def type_id_list_until_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    if p[3]:
        type_id = TypeIdPack(p[2])
    else:
        type_id = p[2]
    for r in result:
        r.append(type_id)
    return result


@glrp.rule('noexcept-specification : "noexcept"  [prec:left,1]"(" constant-expression ")"')
@cxx11
def noexcept_specifier_constant_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return NoExceptSpecifier(p[2])


@glrp.rule('noexcept-specification : "noexcept"  [prec:left,1]"(" "#error" ")"')
@cxx11
def noexcept_specifier_constant_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ExceptionSpecifierError()


@glrp.rule('noexcept-specification : "noexcept" ')
@cxx11
def noexcept_specifier_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return NoExceptSpecifier(None)


@glrp.rule('noexcept-specification? : noexcept-specification')
@cxx11
def noexcept_specifier_opt_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('noexcept-specification? :')
@cxx11
def noexcept_specifier_opt_empty_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.merge('type-id-list')
@cxx98_merge
def ambiguous_type_id_list_ellipsis(
    self: CxxParser, end_declarator_list: List[Any], continue_declarator_list: List[Any]
) -> Any:
    return sum(end_declarator_list + continue_declarator_list, [])


@glrp.merge('type-id-list')
@cxx98_merge
def ambiguous_type_id_list_template(
    self: CxxParser, ambiguous_type_id: List[Any], ambiguous_type_id_list_template: List[Any]
) -> Any:
    return sum(ambiguous_type_id + ambiguous_type_id_list_template, [])
