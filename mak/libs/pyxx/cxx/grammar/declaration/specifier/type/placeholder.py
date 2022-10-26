"""
placeholder-type-specifier:
    type-constraint? auto
    type-constraint? decltype ( auto )
"""

import glrp
from .....parser import cxx11, cxx14, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('placeholder-type-specifier : "auto"')
@cxx11
def placeholder_type_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('placeholder-type-specifier : "decltype" "(" "auto" ")"')
@cxx14
def placeholder_type_specifier_cxx14(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('placeholder-type-specifier : "identifier" [prec:left,1]"auto"')
@glrp.rule(
    'placeholder-type-specifier : template-name [action:begin_template_list]"<" template-argument-list? "%>" [prec:left,1]"auto"'
)
@glrp.rule('placeholder-type-specifier : nested-name-specifier "template"? "identifier" [prec:left,1]"auto"')
@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? template-name [action:begin_template_list]"<" template-argument-list? "%>" [prec:left,1]"auto"'
)
@glrp.rule('placeholder-type-specifier : "identifier" [prec:left,1]"decltype" "(" "auto" ")"')
@glrp.rule(
    'placeholder-type-specifier : template-name [action:begin_template_list]"<" template-argument-list? "%>" [prec:left,1]"decltype" "(" "auto" ")"'
)
@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? "identifier" [prec:left,1]"decltype" "(" "auto" ")"'
)
@glrp.rule(
    'placeholder-type-specifier : nested-name-specifier "template"? template-name [action:begin_template_list]"<" template-argument-list? "%>" [prec:left,1]"decltype" "(" "auto" ")"'
)
@cxx20
def placeholder_type_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser