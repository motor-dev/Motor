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


@glrp.rule('simple-type-specifier : type-name')
# TODO: template? not allowed
@glrp.rule('simple-type-specifier : nested-name-specifier "template"? type-name')
# TODO: already covered
#@glrp.rule('simple-type-specifier : nested-name-specifier "template"? simple-template-id')
@glrp.rule('simple-type-specifier[split:template_decl] : template-name')
# TODO: template? not allowed
@glrp.rule('simple-type-specifier : nested-name-specifier "template"? template-name')
@glrp.rule('simple-type-specifier : "char"')
@glrp.rule('simple-type-specifier : "wchar_t"')
@glrp.rule('simple-type-specifier : "bool"')
@glrp.rule('simple-type-specifier : "short"')
@glrp.rule('simple-type-specifier : "int"')
@glrp.rule('simple-type-specifier : "long"')
@glrp.rule('simple-type-specifier : "signed"')
@glrp.rule('simple-type-specifier : "unsigned"')
@glrp.rule('simple-type-specifier : "float"')
@glrp.rule('simple-type-specifier : "double"')
@glrp.rule('simple-type-specifier : "void"')
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
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('simple-type-specifier : decltype-specifier')
@glrp.rule('simple-type-specifier : placeholder-type-specifier')
@glrp.rule('simple-type-specifier : "char16_t"')
@glrp.rule('simple-type-specifier : "char32_t"')
@glrp.rule('simple-type-specifier-3 : "char16_t"')
@glrp.rule('simple-type-specifier-3 : "char32_t"')
@cxx11
def simple_type_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('simple-type-specifier : "char8_t"')
@glrp.rule('simple-type-specifier-3 : "char8_t"')
@cxx20
def simple_type_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-name : class-name[prec:right,1]')
@glrp.rule('type-name : enum-name')
@glrp.rule('type-name : typedef-name')
@cxx98
def type_name(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from .....parser import CxxParser
