"""
simple-type-specifier:
    nested-name-specifier? type-name
    nested-name-specifier template simple-template-id
    decltype-specifier
    placeholder-type-specifier
    nested-name-specifier? template-name
    char
    char8_t
    char16_t
    char32_t
    wchar_t
    bool
    short
    int
    long
    signed
    unsigned
    float
    double
    void

type-name:
    class-name
    enum-name
    typedef-name
"""

import glrp
from .....parser import cxx98, cxx11, cxx20, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('simple-type-specifier-2 : type-name')
# TODO: template? not allowed
@glrp.rule('simple-type-specifier-2 : nested-name-specifier "template"? type-name')
# TODO: already covered
#@glrp.rule('simple-type-specifier : nested-name-specifier "template"? simple-template-id')
#@glrp.rule('simple-type-specifier-2 : template-name')
# TODO: template? not allowed
#@glrp.rule('simple-type-specifier-2 : nested-name-specifier "template"? template-name')
@glrp.rule('simple-type-specifier-2 : "char"')
@glrp.rule('simple-type-specifier-2 : "wchar_t"')
@glrp.rule('simple-type-specifier-2 : "bool"')
@glrp.rule('simple-type-specifier-2 : "short"')
@glrp.rule('simple-type-specifier-2 : "int"')
@glrp.rule('simple-type-specifier-2 : "long"')
@glrp.rule('simple-type-specifier-2 : "signed"')
@glrp.rule('simple-type-specifier-2 : "unsigned"')
@glrp.rule('simple-type-specifier-2 : "float"')
@glrp.rule('simple-type-specifier-2 : "double"')
@glrp.rule('simple-type-specifier-2 : "void"')
@glrp.rule('simple-type-specifier-3 : "char"')
@glrp.rule('simple-type-specifier-3 : "wchar_t"')
@glrp.rule('simple-type-specifier-3 : "bool"')
@glrp.rule('simple-type-specifier-3 : "short"')
@glrp.rule('simple-type-specifier-3 : "int"')
@glrp.rule('simple-type-specifier-3 : "long"')
@glrp.rule('simple-type-specifier-3 : "signed"')
@glrp.rule('simple-type-specifier-3 : "unsigned"')
@glrp.rule('simple-type-specifier-3 : "float"')
@glrp.rule('simple-type-specifier-3 : "double"')
@glrp.rule('simple-type-specifier-3 : "void"')
@cxx98
def simple_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('simple-type-specifier-2 : decltype-specifier')
@glrp.rule('simple-type-specifier-2 : placeholder-type-specifier')
@glrp.rule('simple-type-specifier-2 : "char16_t"')
@glrp.rule('simple-type-specifier-2 : "char32_t"')
@glrp.rule('simple-type-specifier-3 : "char16_t"')
@glrp.rule('simple-type-specifier-3 : "char32_t"')
@cxx11
def simple_type_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('simple-type-specifier-2 : "char8_t"')
@cxx20
def simple_type_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


#@glrp.rule('type-name : class-name[prec:right,1]')
#@glrp.rule('type-name : enum-name')
#@glrp.rule('type-name : typedef-name')
@glrp.rule('type-name[prec:right,1] : identifier')
@glrp.rule('type-name[prec:right,1] : simple-template-id')
@cxx98
def type_name(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from .....parser import CxxParser
