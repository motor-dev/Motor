"""
type-requirement:
    typename nested-name-specifier? type-name ;
"""

import glrp
from .....parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('type-requirement : "typename" "identifier" ";"')
@glrp.rule(
    'type-requirement : "typename" template-name [action:begin_template_list]"<" template-argument-list? "%>" ";"'
)
# TODO: template not allowed
@glrp.rule('type-requirement : "typename" nested-name-specifier template? "identifier" ";"')
@glrp.rule(
    'type-requirement : "typename" nested-name-specifier template? template-name [action:begin_template_list]"<" template-argument-list? "%>" ";"'
)
@cxx20
def type_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser
