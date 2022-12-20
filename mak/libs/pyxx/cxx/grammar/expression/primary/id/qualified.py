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
from .....parse import cxx98, cxx11
from ......ast.reference import Reference, Id, RootId, TemplateId
from motor_typing import TYPE_CHECKING


@glrp.rule('qualified-id : nested-name-specifier "template"? unqualified-id')
@cxx98
def qualified_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    name_list = p[0]
    name_list.append((p[1], p[2]))
    return name_list


@glrp.rule('nested-name-specifier : "::"')
@cxx98
def nested_name_specifier_root(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [(False, RootId())]


@glrp.rule('nested-name-specifier : nested-name-specifier-element')
@cxx98
def nested_name_specifier_element(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [(False, p[0])]


@glrp.rule('nested-name-specifier : nested-name-specifier "template"? "identifier" [prec:left,2]"::"')
@cxx98
def nested_name_specifier_identifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append((p[1], Id(p[2].value)))
    return result


@glrp.rule(
    'nested-name-specifier : nested-name-specifier "template"? template-name "<" template-argument-list? "#>" [prec:left,2]"::"'
)
@cxx98
def nested_name_specifier_template(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append((p[1], TemplateId(p[2], p[4])))
    return result


#@glrp.rule('nested-name-specifier-element : type-name [prec:left,2]"::"')
#@glrp.rule('nested-name-specifier-element : namespace-name [prec:left,2]"::"')
@glrp.rule('nested-name-specifier-element : "identifier" [prec:left,2]"::"')
@cxx98
def nested_name_specifier_element_identifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Id(p[0].value)


@glrp.rule('nested-name-specifier-element : template-name "<" template-argument-list? "#>" [prec:left,2]"::"')
@cxx98
def nested_name_specifier_element_template(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TemplateId(p[0], p[2])


@glrp.rule('nested-name-specifier : decltype-specifier [prec:left,2]"::"')
@cxx11
def nested_name_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [(False, p[0])]


@glrp.rule('"::"? : "::"')
@cxx98
def scope(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [(False, RootId())]


@glrp.rule('"::"? : ')
@cxx98
def scope_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return []


if TYPE_CHECKING:
    from typing import Any, List
    from .....parse import CxxParser