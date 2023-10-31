"""
type-requirement:
    typename nested-name-specifier? type-name ;
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx20
from ......ast.reference import TemplateId, TemplateSpecifierId, Id, Reference, _Id
from ......ast.type import TypeSpecifierReference
from ......ast.constraints import TypeRequirement, ErrorRequirement


@glrp.rule('type-requirement : "typename" "identifier" ";"')
@cxx20
def type_requirement_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return TypeRequirement(TypeSpecifierReference(Reference([Id(p[1].value)])))


@glrp.rule('type-requirement : "typename" template-name "<" template-argument-list? "#>" ";"')
@cxx20
def type_requirement_template_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return TypeRequirement(TypeSpecifierReference(Reference([TemplateId(p[1], p[3])])))


@glrp.rule('type-requirement : "typename" nested-name-specifier template? "identifier" ";"')
@cxx20
def type_requirement_nested_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    id = Id(p[3].value)    # type: _Id
    if p[2]:
        id = TemplateSpecifierId(id)
    return TypeRequirement(TypeSpecifierReference(Reference(p[1] + [id])))


@glrp.rule(
    'type-requirement : "typename" nested-name-specifier template? template-name "<" template-argument-list? "#>" ";"'
)
@cxx20
def type_requirement_nested_template_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    id = TemplateId(p[3], p[5])    # type: _Id
    if p[2]:
        id = TemplateSpecifierId(id)
    return TypeRequirement(TypeSpecifierReference(Reference(p[1] + [id])))


@glrp.rule('type-requirement : "typename" "#error" ";"')
@cxx20
def type_requirement_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorRequirement()
