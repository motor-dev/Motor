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
from .....parser import cxx98, cxx11, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('qualified-id : nested-name-specifier "template"? unqualified-id')
@cxx98
def qualified_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('nested-name-specifier : "::"')
@glrp.rule('nested-name-specifier : nested-name-specifier-element')
@glrp.rule('nested-name-specifier : nested-name-specifier "template"? "identifier" [prec:left,2]"::"')
@glrp.rule(
    'nested-name-specifier : nested-name-specifier "template"? template-name [action:begin_template_list]"<" template-argument-list? "%>" [prec:left,2]"::"'
)
@cxx98
def nested_name_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


#@glrp.rule('nested-name-specifier-element : type-name [prec:left,2]"::"')
#@glrp.rule('nested-name-specifier-element : namespace-name [prec:left,2]"::"')
@glrp.rule('nested-name-specifier-element : "identifier" [prec:left,2]"::"')
@glrp.rule(
    'nested-name-specifier-element : template-name [action:begin_template_list]"<" template-argument-list? "%>" [prec:left,2]"::"'
)
@cxx98
def nested_name_specifier_element(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('nested-name-specifier : decltype-specifier [prec:left,2]"::"')
@cxx11
def nested_name_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('"::"? : "::"')
@glrp.rule('"::"? : ')
@cxx98
def scope_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from .....parser import CxxParser