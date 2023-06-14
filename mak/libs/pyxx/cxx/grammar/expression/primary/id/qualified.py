"""
qualified-id:
    nested-name-specifier template? unqualified-id

nested-name-specifier:
    ::
    type-name ::
    namespace-name ::
    decltype-specifier ::
    nested-name-specifier identifier ::
    nested-name-specifier template? simple-template-id ::
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx98, cxx11
from ......ast.reference import Id, RootId, TemplateId, TemplateSpecifierId, _Id


@glrp.rule('qualified-id : nested-name-specifier "template"? unqualified-id')
@cxx98
def qualified_id(self: CxxParser, p: glrp.Production) -> Any:
    name_list = p[0]
    id = p[2]  # type: _Id
    if p[1]:
        id = TemplateSpecifierId(id)
    name_list.append(id)
    return name_list


@glrp.rule('nested-name-specifier : "::"')
@cxx98
def nested_name_specifier_root(self: CxxParser, p: glrp.Production) -> Any:
    return [RootId()]


@glrp.rule('nested-name-specifier : nested-name-specifier-element')
@cxx98
def nested_name_specifier_element(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]]


@glrp.rule('nested-name-specifier : nested-name-specifier "template"? "identifier" [prec:left,2]"::"')
@cxx98
def nested_name_specifier_identifier(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    id = Id(p[2].value)  # type: _Id
    if p[1]:
        id = TemplateSpecifierId(id)
    result.append(id)
    return result


@glrp.rule(
    'nested-name-specifier : nested-name-specifier "template"? template-name "<" template-argument-list? "#>" [prec:left,2]"::"'
)
@cxx98
def nested_name_specifier_template(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    id = TemplateId(p[2], p[4])  # type: _Id
    if p[1]:
        id = TemplateSpecifierId(id)
    result.append(id)
    return result


# @glrp.rule('nested-name-specifier-element : type-name [prec:left,2]"::"')
# @glrp.rule('nested-name-specifier-element : namespace-name [prec:left,2]"::"')
@glrp.rule('nested-name-specifier-element : "identifier" [prec:left,2]"::"')
@cxx98
def nested_name_specifier_element_identifier(self: CxxParser, p: glrp.Production) -> Any:
    return Id(p[0].value)


@glrp.rule('nested-name-specifier-element : template-name "<" template-argument-list? "#>" [prec:left,2]"::"')
@cxx98
def nested_name_specifier_element_template(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateId(p[0], p[2])


@glrp.rule('nested-name-specifier : decltype-specifier [prec:left,2]"::"')
@cxx11
def nested_name_specifier_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]]


@glrp.rule('"::"? : "::"')
@cxx98
def scope(self: CxxParser, p: glrp.Production) -> Any:
    return [RootId()]


@glrp.rule('"::"? : ')
@cxx98
def scope_opt(self: CxxParser, p: glrp.Production) -> Any:
    return []
