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
from .....parser import cxx98, cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('qualified-id : nested-name-specifier "template"? unqualified-id')
@cxx98
def qualified_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('nested-name-specifier : [split]"::"')
@glrp.rule('nested-name-specifier : type-name [prec:left,1]"::"')
@glrp.rule('nested-name-specifier : namespace-name [prec:left,1]"::"')
@glrp.rule('nested-name-specifier : nested-name-specifier "template"? "identifier" [prec:left,1]"::"')
@glrp.rule('nested-name-specifier : nested-name-specifier "template"? simple-template-id [prec:left,1]"::"')
@cxx98
def nested_name_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('nested-name-specifier : decltype-specifier [prec:left,1]"::"')
@cxx11
def nested_name_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('"::"? : "::"')
@glrp.rule('"::"? : ')
@cxx98
def scope_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser