"""
template-parameter:
    type-parameter
    parameter-declaration

type-parameter:
    type-parameter-key ...? identifier?
    type-parameter-key identifier? = type-id
    type-constraint ...? identifier?
    type-constraint identifier? = type-id
    template-head type-parameter-key ...? identifier?
    template-head type-parameter-key identifier? = id-expression

type-parameter-key:
    class
    typename

type-constraint:
    nested-name-specifier? concept-name
    nested-name-specifier? concept-name < template-argument-list? >
"""

import glrp
from ...parser import cxx98, cxx11, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('template-parameter : type-parameter')
@glrp.rule('template-parameter : parameter-declaration')
@cxx98
def template_parameter(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


# TODO: attribute-specifier-seq? not allowed
@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "identifier"? "=" type-id')
@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "identifier"? "=" id-expression')
@cxx98
def type_parameter(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


# TODO: attribute-specifier-seq? not allowed
@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "..." "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "..." "identifier"?')
@cxx11
def type_parameter_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


# TODO: attribute-specifier-seq? not allowed
@glrp.rule('type-parameter : attribute-specifier-seq? type-constraint "..."? "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? type-constraint "identifier"? "=" type-id')
@cxx20
def type_parameter_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


#@glrp.rule('type-parameter-key[split] : "class"')
# TODO: only class allowed
@glrp.rule('type-parameter-key[split] : class-key')
@glrp.rule('type-parameter-key[split] : "typename"')
@cxx98
def type_parameter_key(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-constraint : nested-name-specifier? concept-name')
@glrp.rule('type-constraint : nested-name-specifier? concept-name "<" template-argument-list? ">"')
@cxx20
def type_constraint_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser