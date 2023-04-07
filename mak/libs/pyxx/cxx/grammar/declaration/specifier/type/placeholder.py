"""
placeholder-type-specifier:
    type-constraint? auto
    type-constraint? decltype ( auto )
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx11, cxx14, cxx20
from ......ast.type import AutoTypeSpecifier, DecltypeAutoTypeSpecifier, ConstrainedTypeSpecifier
from ......ast.reference import Id, TemplateId, Reference, TemplateSpecifierId, _Id


@glrp.rule('placeholder-type-specifier : "auto"')
@cxx11
def placeholder_type_specifier_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return AutoTypeSpecifier()


@glrp.rule('placeholder-type-specifier : "decltype" "(" "auto" ")"')
@glrp.rule('placeholder-type-specifier : "decltype-macro" "(" "auto" ")"')
@cxx14
def placeholder_type_specifier_cxx14(self: CxxParser, p: glrp.Production) -> Any:
    return DecltypeAutoTypeSpecifier(p[0].text())


@glrp.rule('placeholder-type-specifier : "identifier" [prec:left,1]"auto"')
@cxx20
def placeholder_type_specifier_constraint_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ConstrainedTypeSpecifier(Reference([Id(p[0].value)]), AutoTypeSpecifier())


@glrp.rule('placeholder-type-specifier : template-name "<" template-argument-list? "#>" [prec:left,1]"auto"')
@cxx20
def placeholder_type_specifier_constraint_template_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ConstrainedTypeSpecifier(Reference([TemplateId(p[0], p[2])]), AutoTypeSpecifier())


@glrp.rule('placeholder-type-specifier : nested-name-specifier "template"? "identifier" [prec:left,1]"auto"')
@cxx20
def placeholder_type_specifier_constraint_nested_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    id = Id(p[2].value)    # type: _Id
    if p[1]:
        id = TemplateSpecifierId(id)
    return ConstrainedTypeSpecifier(Reference(p[0] + [id]), AutoTypeSpecifier())


@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? template-name "<" template-argument-list? "#>" [prec:left,1]"auto"'
)
@cxx20
def placeholder_type_specifier_constraint_template_nested_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    id = TemplateId(p[2], p[4])    # type: _Id
    if p[1]:
        id = TemplateSpecifierId(id)
    return ConstrainedTypeSpecifier(Reference(p[0] + [id]), AutoTypeSpecifier())


@glrp.rule('placeholder-type-specifier : "identifier" [prec:left,1]"decltype" "(" "auto" ")"')
@glrp.rule('placeholder-type-specifier : "identifier" [prec:left,1]"decltype-macro" "(" "auto" ")"')
@cxx20
def placeholder_type_specifier_constraint_decltype_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ConstrainedTypeSpecifier(Reference([Id(p[0].value)]), DecltypeAutoTypeSpecifier(p[1].text()))


@glrp.rule(
    'placeholder-type-specifier : template-name "<" template-argument-list? "#>" [prec:left,1]"decltype" "(" "auto" ")"'
)
@glrp.rule(
    'placeholder-type-specifier : template-name "<" template-argument-list? "#>" [prec:left,1]"decltype-macro" "(" "auto" ")"'
)
@cxx20
def placeholder_type_specifier_constraint_template_decltype_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ConstrainedTypeSpecifier(Reference([TemplateId(p[0], p[2])]), DecltypeAutoTypeSpecifier(p[4].text()))


@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? "identifier" [prec:left,1]"decltype" "(" "auto" ")"'
)
@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? "identifier" [prec:left,1]"decltype-macro" "(" "auto" ")"'
)
@cxx20
def placeholder_type_specifier_constraint_nested_decltype_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    id = Id(p[2].value)    # type: _Id
    if p[1]:
        id = TemplateSpecifierId(id)
    return ConstrainedTypeSpecifier(Reference(p[0] + [id]), DecltypeAutoTypeSpecifier(p[3].text()))


@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? template-name "<" template-argument-list? "#>" [prec:left,1]"decltype" "(" "auto" ")"'
)
@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? template-name "<" template-argument-list? "#>" [prec:left,1]"decltype-macro" "(" "auto" ")"'
)
@cxx20
def placeholder_type_specifier_constraint_template_nested_decltype_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    id = TemplateId(p[2], p[4])    # type: _Id
    if p[1]:
        id = TemplateSpecifierId(id)
    return ConstrainedTypeSpecifier(Reference(p[0] + [id]), DecltypeAutoTypeSpecifier(p[6].text()))
