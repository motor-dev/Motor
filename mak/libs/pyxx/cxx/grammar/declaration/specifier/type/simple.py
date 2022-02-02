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
@cxx98
def simple_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('simple-type-specifier : decltype-specifier')
@glrp.rule('simple-type-specifier : placeholder-type-specifier')
@glrp.rule('simple-type-specifier : "char16_t"')
@glrp.rule('simple-type-specifier : "char32_t"')
@cxx11
def simple_type_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('simple-type-specifier : "char8_t"')
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


#@glrp.merge('type-name')
#@cxx98_merge
#def generic_type_name(self, template_name, class_name, enum_name, typedef_name):
#    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
#    pass
#
#
#@glrp.merge('simple-type-specifier')
#@cxx98_merge
#def generic_simple_type_specifier(self, generic_nested_name_specifier, generic_type_name, template_name, concept_name):
#    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
#    pass
#
#
#@glrp.merge('simple-type-specifier')
#@cxx98_merge
#def template_simple_type_specifier(self, class_template_id, typedef_template_id):
#    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
#    pass

if TYPE_CHECKING:
    from typing import Optional
    from .....parser import CxxParser
