"""
type-requirement:
    typename nested-name-specifier? type-name ;
"""

import glrp
from .....parse import cxx20
from ......ast.reference import TemplateId, Id, Reference
from ......ast.type import TypeSpecifierReference
from ......ast.constraints import TypeRequirement
from motor_typing import TYPE_CHECKING


@glrp.rule('type-requirement : "typename" "identifier" ";"')
@cxx20
def type_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeRequirement(TypeSpecifierReference(Reference([(False, Id(p[1].value))]), False))


@glrp.rule('type-requirement : "typename" template-name "<" template-argument-list? "#>" ";"')
@cxx20
def type_requirement_template_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeRequirement(TypeSpecifierReference(Reference([(False, TemplateId(p[1], p[3]))]), False))


@glrp.rule('type-requirement : "typename" nested-name-specifier template? "identifier" ";"')
@cxx20
def type_requirement_nested_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeRequirement(TypeSpecifierReference(Reference(p[1] + [(p[2], Id(p[3].value))]), False))


@glrp.rule(
    'type-requirement : "typename" nested-name-specifier template? template-name "<" template-argument-list? "#>" ";"'
)
@cxx20
def type_requirement_nested_template_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeRequirement(TypeSpecifierReference(Reference(p[1] + [(p[2], TemplateId(p[3], p[5]))]), False))


if TYPE_CHECKING:
    from typing import Any
    from .....parse import CxxParser
