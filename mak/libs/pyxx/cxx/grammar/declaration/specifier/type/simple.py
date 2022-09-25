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


#@glrp.rule('simple-type-specifier-2 : type-name')
@glrp.rule('simple-type-specifier-2 : "identifier"[split:id_nontemplate]')
@glrp.rule(
    'simple-type-specifier-2 : template-name [action:begin_template_list]"<" template-argument-list? "%>"[split:id_nontemplate]'
)
# TODO: template? not allowed
@glrp.rule('simple-type-specifier-2 : nested-name-specifier "template"? identifier [split:id_nontemplate]')
@glrp.rule(
    'simple-type-specifier-2 : nested-name-specifier "template"? template-name [action:begin_template_list]"<" template-argument-list? "%>"[split:id_nontemplate]'
)
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
@glrp.rule('simple-type-specifier-cast : "identifier"[split:simple_type_specifier_cast]')
@glrp.rule(
    'simple-type-specifier-cast : template-name [action:begin_template_list]"<" template-argument-list? "%>" [split:simple_type_specifier_cast]'
)
# TODO: template? not allowed
@glrp.rule(
    'simple-type-specifier-cast : nested-name-specifier "template"? identifier [split:simple_type_specifier_cast]'
)
@glrp.rule(
    'simple-type-specifier-cast : nested-name-specifier "template"? template-name [action:begin_template_list]"<" template-argument-list? "%>" [split:simple_type_specifier_cast]'
)
# TODO: already covered
#@glrp.rule('simple-type-specifier : nested-name-specifier "template"? simple-template-id')
#@glrp.rule('simple-type-specifier-2 : template-name')
# TODO: template? not allowed
#@glrp.rule('simple-type-specifier-2 : nested-name-specifier "template"? template-name')
@glrp.rule('simple-type-specifier-cast : "char"')
@glrp.rule('simple-type-specifier-cast : "wchar_t"')
@glrp.rule('simple-type-specifier-cast : "bool"')
@glrp.rule('simple-type-specifier-cast : "short"')
@glrp.rule('simple-type-specifier-cast : "int"')
@glrp.rule('simple-type-specifier-cast : "long"')
@glrp.rule('simple-type-specifier-cast : "signed"')
@glrp.rule('simple-type-specifier-cast : "unsigned"')
@glrp.rule('simple-type-specifier-cast : "float"')
@glrp.rule('simple-type-specifier-cast : "double"')
@glrp.rule('simple-type-specifier-cast : "void"')
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
@glrp.rule('simple-type-specifier-cast : decltype-specifier')
@glrp.rule('simple-type-specifier-cast : placeholder-type-specifier')
@glrp.rule('simple-type-specifier-cast : "char16_t"')
@glrp.rule('simple-type-specifier-cast : "char32_t"')
@cxx11
def simple_type_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('simple-type-specifier-2 : "char8_t"')
@glrp.rule('simple-type-specifier-cast : "char8_t"')
@cxx20
def simple_type_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


#@glrp.rule('type-name : class-name')
#@glrp.rule('type-name : enum-name')
#@glrp.rule('type-name : typedef-name')
#@cxx98
#def type_name(self, p):
#    # type: (CxxParser, glrp.Production) -> Any
#    pass

if TYPE_CHECKING:
    from typing import Any, List
    from .....parser import CxxParser
