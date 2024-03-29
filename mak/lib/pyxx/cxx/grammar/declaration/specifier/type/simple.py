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
from typing import Any, List
from .....parse import CxxParser, cxx98, cxx11, cxx20, cxx98_merge
from ......ast.reference import TemplateId, Id, Reference, TemplateSpecifierId, _Id
from ......ast.type import PrimitiveTypeSpecifiers, TypeSpecifierReference, AmbiguousTypeSpecifier


# @glrp.rule('simple-type-specifier-2 : type-name')
@glrp.rule('simple-type-specifier-2 : "identifier"[split:id_nontemplate]')
@glrp.rule('simple-type-specifier-cast : "identifier"[split:simple_type_specifier_cast]')
@cxx98
def simple_type_specifier_identifier(self: CxxParser, p: glrp.Production) -> Any:
    return TypeSpecifierReference(Reference([Id(p[0].position, p[0].value)]))


@glrp.rule('simple-type-specifier-2 : template-name "<" template-argument-list? "#>"')
@glrp.rule(
    'simple-type-specifier-cast : template-name "<" template-argument-list? "#>" [split:simple_type_specifier_cast]'
)
@cxx98
def simple_type_specifier_template(self: CxxParser, p: glrp.Production) -> Any:
    return TypeSpecifierReference(Reference([TemplateId(p[3].position[1], p[0], p[2])]))


# TODO: template? not allowed
@glrp.rule('simple-type-specifier-2 : nested-name-specifier "template"? identifier [split:id_nontemplate]')
@glrp.rule(
    'simple-type-specifier-cast : nested-name-specifier "template"? identifier [split:simple_type_specifier_cast]'
)
@cxx98
def simple_type_specifier_qualified_name(self: CxxParser, p: glrp.Production) -> Any:
    id = Id(p[2].position, p[2].value)  # type: _Id
    if p[1]:
        id = TemplateSpecifierId(p[1].position, id)
    return TypeSpecifierReference(Reference(p[0] + [id]))


@glrp.rule('simple-type-specifier-2 : nested-name-specifier "template"? template-name "<" template-argument-list? "#>"')
@glrp.rule(
    'simple-type-specifier-cast : nested-name-specifier "template"? template-name "<" template-argument-list? "#>" [split:simple_type_specifier_cast]'
)
@cxx98
def simple_type_specifier_qualified_template(self: CxxParser, p: glrp.Production) -> Any:
    id = TemplateId(p[5].position[1], p[2], p[4])  # type: _Id
    if p[1]:
        id = TemplateSpecifierId(p[1].position, id)
    return TypeSpecifierReference(Reference(p[0] + [id]))


@glrp.rule('simple-type-specifier-2 : "char"')
@glrp.rule('simple-type-specifier-3 : "char"')
@glrp.rule('simple-type-specifier-cast : "char"')
@cxx98
def simple_type_specifier_primitive_char(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.CHAR


@glrp.rule('simple-type-specifier-2 : "wchar_t"')
@glrp.rule('simple-type-specifier-3 : "wchar_t"')
@glrp.rule('simple-type-specifier-cast : "wchar_t"')
@cxx98
def simple_type_specifier_primitive_wchar_t(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.WCHAR_T


@glrp.rule('simple-type-specifier-2 : "bool"')
@glrp.rule('simple-type-specifier-3 : "bool"')
@glrp.rule('simple-type-specifier-cast : "bool"')
@cxx98
def simple_type_specifier_primitive_bool(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.BOOL


@glrp.rule('simple-type-specifier-2 : "short"')
@glrp.rule('simple-type-specifier-3 : "short"')
@glrp.rule('simple-type-specifier-cast : "short"')
@cxx98
def simple_type_specifier_primitive_short(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.SHORT


@glrp.rule('simple-type-specifier-2 : "int"')
@glrp.rule('simple-type-specifier-3 : "int"')
@glrp.rule('simple-type-specifier-cast : "int"')
@cxx98
def simple_type_specifier_primitive_int(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.INT


@glrp.rule('simple-type-specifier-2 : "__int128"')
@glrp.rule('simple-type-specifier-3 : "__int128"')
@glrp.rule('simple-type-specifier-cast : "__int128"')
@cxx98
def simple_type_specifier_primitive_int128(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.INT128


@glrp.rule('simple-type-specifier-2 : "long"')
@glrp.rule('simple-type-specifier-3 : "long"')
@glrp.rule('simple-type-specifier-cast : "long"')
@cxx98
def simple_type_specifier_primitive_long(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.LONG


@glrp.rule('simple-type-specifier-2 : "signed"')
@glrp.rule('simple-type-specifier-3 : "signed"')
@glrp.rule('simple-type-specifier-cast : "signed"')
@cxx98
def simple_type_specifier_primitive_signed(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.SIGNED


@glrp.rule('simple-type-specifier-2 : "unsigned"')
@glrp.rule('simple-type-specifier-3 : "unsigned"')
@glrp.rule('simple-type-specifier-cast : "unsigned"')
@cxx98
def simple_type_specifier_primitive_unsigned(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.UNSIGNED


@glrp.rule('simple-type-specifier-2 : "float"')
@glrp.rule('simple-type-specifier-3 : "float"')
@glrp.rule('simple-type-specifier-cast : "float"')
@cxx98
def simple_type_specifier_primitive_float(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.FLOAT


@glrp.rule('simple-type-specifier-2 : "double"')
@glrp.rule('simple-type-specifier-3 : "double"')
@glrp.rule('simple-type-specifier-cast : "double"')
@cxx98
def simple_type_specifier_primitive_double(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.DOUBLE


@glrp.rule('simple-type-specifier-2 : "void"')
@glrp.rule('simple-type-specifier-3 : "void"')
@glrp.rule('simple-type-specifier-cast : "void"')
@cxx98
def simple_type_specifier_primitive_void(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.VOID


@glrp.rule('simple-type-specifier-2 : decltype-specifier')
@glrp.rule('simple-type-specifier-cast : decltype-specifier')
@cxx98
def simple_type_specifier_decltype_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('simple-type-specifier-2 : placeholder-type-specifier')
@glrp.rule('simple-type-specifier-cast : placeholder-type-specifier')
@cxx11
def simple_type_specifier_placeholder_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('simple-type-specifier-2 : "char16_t"')
@glrp.rule('simple-type-specifier-3 : "char16_t"')
@glrp.rule('simple-type-specifier-cast : "char16_t"')
@cxx11
def simple_type_specifier_primitive_char16_t_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.CHAR16_T


@glrp.rule('simple-type-specifier-2 : "char32_t"')
@glrp.rule('simple-type-specifier-3 : "char32_t"')
@glrp.rule('simple-type-specifier-cast : "char32_t"')
@cxx11
def simple_type_specifier_primitive_char32_t_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.CHAR32_T


@glrp.rule('simple-type-specifier-2 : "char8_t"')
@glrp.rule('simple-type-specifier-3 : "char8_t"')
@glrp.rule('simple-type-specifier-cast : "char8_t"')
@cxx20
def simple_type_specifier_char8_t_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return PrimitiveTypeSpecifiers.CHAR8_T


@glrp.merge('simple-type-specifier-2')
@cxx98_merge
def ambiguous_simple_type_specifier_2(
        self: CxxParser, ambiguous_template_argument_list_ellipsis: List[Any], ambiguous_expression: List[Any]
) -> Any:
    return AmbiguousTypeSpecifier(ambiguous_template_argument_list_ellipsis + ambiguous_expression)


@glrp.merge('simple-type-specifier-cast')
@cxx98_merge
def ambiguous_simple_type_specifier_cast(
        self: CxxParser, ambiguous_template_argument_list_ellipsis: List[Any], ambiguous_expression: List[Any]
) -> Any:
    return AmbiguousTypeSpecifier(ambiguous_template_argument_list_ellipsis + ambiguous_expression)
