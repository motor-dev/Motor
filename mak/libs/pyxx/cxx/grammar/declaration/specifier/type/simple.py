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


@glrp.rule('simple-type-specifier-def : type-name')
# TODO: template? not allowed
@glrp.rule('simple-type-specifier-def : nested-name-specifier "template"? type-name')
# TODO: already covered
#@glrp.rule('simple-type-specifier : nested-name-specifier "template"? simple-template-id')
@glrp.rule('simple-type-specifier-def : template-name')
# TODO: template? not allowed
@glrp.rule('simple-type-specifier-def : nested-name-specifier "template"? template-name')
@glrp.rule('simple-type-specifier-def : "char"')
@glrp.rule('simple-type-specifier-def : "wchar_t"')
@glrp.rule('simple-type-specifier-def : "bool"')
@glrp.rule('simple-type-specifier-def : "short"')
@glrp.rule('simple-type-specifier-def : "int"')
@glrp.rule('simple-type-specifier-def : "long"')
@glrp.rule('simple-type-specifier-def : "signed"')
@glrp.rule('simple-type-specifier-def : "unsigned"')
@glrp.rule('simple-type-specifier-def : "float"')
@glrp.rule('simple-type-specifier-def : "double"')
@glrp.rule('simple-type-specifier-def : "void"')
@glrp.rule('simple-type-specifier-tail : "char"')
@glrp.rule('simple-type-specifier-tail : "wchar_t"')
@glrp.rule('simple-type-specifier-tail : "bool"')
@glrp.rule('simple-type-specifier-tail : "short"')
@glrp.rule('simple-type-specifier-tail : "int"')
@glrp.rule('simple-type-specifier-tail : "long"')
@glrp.rule('simple-type-specifier-tail : "signed"')
@glrp.rule('simple-type-specifier-tail : "unsigned"')
@glrp.rule('simple-type-specifier-tail : "float"')
@glrp.rule('simple-type-specifier-tail : "double"')
@cxx98
def simple_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('simple-type-specifier-def : decltype-specifier')
@glrp.rule('simple-type-specifier-def : placeholder-type-specifier')
@glrp.rule('simple-type-specifier-def : "char16_t"')
@glrp.rule('simple-type-specifier-def : "char32_t"')
@glrp.rule('simple-type-specifier-tail : "char16_t"')
@glrp.rule('simple-type-specifier-tail : "char32_t"')
@cxx11
def simple_type_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('simple-type-specifier-def : "char8_t"')
@glrp.rule('simple-type-specifier-tail : "char8_t"')
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


@glrp.merge('type-name')
@cxx98_merge
def ambiguous_type_name(self, class_name, enum_name, typedef_name):
    # type: (CxxParser, Any, Any, Any) -> Any
    pass


@glrp.merge('type-name')
@cxx98_merge
def ambiguous_template_type_name(self, class_template_id, typedef_template_id):
    # type: (CxxParser, Any, Any) -> Any
    pass


@glrp.merge('simple-type-specifier-def')
@cxx98_merge
def ambiguous_simple_type_specifier(self, ambiguous_type_name, ambiguous_type_constraint, template_name):
    # type: (CxxParser, Any, Any, Any) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser
