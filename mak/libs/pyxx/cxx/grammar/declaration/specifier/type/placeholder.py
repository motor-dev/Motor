"""
placeholder-type-specifier:
    type-constraint? auto
    type-constraint? decltype ( auto )
"""

import glrp
from .....parse import cxx11, cxx14, cxx20
from ......ast.type import AutoTypeSpecifier, DecltypeAutoTypeSpecifier, ConstrainedTypeSpecifier
from ......ast.reference import Id, TemplateId, Reference
from motor_typing import TYPE_CHECKING


@glrp.rule('placeholder-type-specifier : "auto"')
@cxx11
def placeholder_type_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AutoTypeSpecifier()


@glrp.rule('placeholder-type-specifier : "decltype" "(" "auto" ")"')
@glrp.rule('placeholder-type-specifier : "decltype-macro" "(" "auto" ")"')
@cxx14
def placeholder_type_specifier_cxx14(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DecltypeAutoTypeSpecifier(p[0].text())


@glrp.rule('placeholder-type-specifier : "identifier" [prec:left,1]"auto"')
@cxx20
def placeholder_type_specifier_constraint_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConstrainedTypeSpecifier(Reference([(False, Id(p[0].value))]), AutoTypeSpecifier())


@glrp.rule('placeholder-type-specifier : template-name "<" template-argument-list? "#>" [prec:left,1]"auto"')
@cxx20
def placeholder_type_specifier_constraint_template_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConstrainedTypeSpecifier(Reference([(False, TemplateId(p[0], p[2]))]), AutoTypeSpecifier())


@glrp.rule('placeholder-type-specifier : nested-name-specifier "template"? "identifier" [prec:left,1]"auto"')
@cxx20
def placeholder_type_specifier_constraint_nested_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConstrainedTypeSpecifier(Reference(p[0] + [(p[1], Id(p[2].value))]), AutoTypeSpecifier())


@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? template-name "<" template-argument-list? "#>" [prec:left,1]"auto"'
)
@cxx20
def placeholder_type_specifier_constraint_template_nested_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConstrainedTypeSpecifier(Reference(p[0] + [(p[1], TemplateId(p[2], p[4]))]), AutoTypeSpecifier())


@glrp.rule('placeholder-type-specifier : "identifier" [prec:left,1]"decltype" "(" "auto" ")"')
@glrp.rule('placeholder-type-specifier : "identifier" [prec:left,1]"decltype-macro" "(" "auto" ")"')
@cxx20
def placeholder_type_specifier_constraint_decltype_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConstrainedTypeSpecifier(Reference([(False, Id(p[0].value))]), DecltypeAutoTypeSpecifier(p[1].text()))


@glrp.rule(
    'placeholder-type-specifier : template-name "<" template-argument-list? "#>" [prec:left,1]"decltype" "(" "auto" ")"'
)
@glrp.rule(
    'placeholder-type-specifier : template-name "<" template-argument-list? "#>" [prec:left,1]"decltype-macro" "(" "auto" ")"'
)
@cxx20
def placeholder_type_specifier_constraint_template_decltype_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConstrainedTypeSpecifier(
        Reference([(False, TemplateId(p[0], p[2]))]), DecltypeAutoTypeSpecifier(p[4].text())
    )


@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? "identifier" [prec:left,1]"decltype" "(" "auto" ")"'
)
@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? "identifier" [prec:left,1]"decltype-macro" "(" "auto" ")"'
)
@cxx20
def placeholder_type_specifier_constraint_nested_decltype_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConstrainedTypeSpecifier(Reference(p[0] + [(p[1], Id(p[2].value))]), DecltypeAutoTypeSpecifier(p[3].text()))


@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? template-name "<" template-argument-list? "#>" [prec:left,1]"decltype" "(" "auto" ")"'
)
@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? template-name "<" template-argument-list? "#>" [prec:left,1]"decltype-macro" "(" "auto" ")"'
)
@cxx20
def placeholder_type_specifier_constraint_template_nested_decltype_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConstrainedTypeSpecifier(
        Reference(p[0] + [(p[1], TemplateId(p[2], p[4]))]), DecltypeAutoTypeSpecifier(p[6].text())
    )


if TYPE_CHECKING:
    from typing import Any
    from .....parse import CxxParser