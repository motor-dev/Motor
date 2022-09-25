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
from ...parser import cxx98, cxx11, cxx20, cxx98_merge, cxx20_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('template-parameter : begin-type-parameter type-parameter')
@glrp.rule('template-parameter : begin-parameter parameter-declaration')
@cxx98
def template_parameter(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


# amendment: @glrp.rule('type-parameter : type-parameter-key "identifier"?')
# amendment: @glrp.rule('type-parameter : type-parameter-key "identifier"? "=" type-id')
# amendment: @glrp.rule('type-parameter : template-head type-parameter-key "identifier"?')
# amendment: @glrp.rule('type-parameter : template-head type-parameter-key "identifier"? "=" id-expression')
@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "identifier"? "=" type-id')
@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "identifier"? "=" id-expression')
@cxx98
def type_parameter(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # TODO: attribute-specifier-seq? not allowed
    pass


# amendment: @glrp.rule('type-parameter : type-parameter-key "..." "identifier"?')
# amendment: @glrp.rule('type-parameter : template-head type-parameter-key "..." "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "..." "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "..." "identifier"?')
@cxx11
def type_parameter_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # TODO: attribute-specifier-seq? not allowed
    pass


# amendment: @glrp.rule('type-parameter : type-constraint "identifier"?')
# amendment: @glrp.rule('type-parameter : type-constraint "..." "identifier"?')
# amendment: @glrp.rule('type-parameter : type-constraint "identifier"? "=" type-id')
@glrp.rule('type-parameter : attribute-specifier-seq? type-constraint "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? type-constraint "..." "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? type-constraint "identifier"? "=" type-id')
@cxx20
def type_parameter_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # TODO: attribute-specifier-seq? not allowed
    pass


@glrp.rule('type-parameter-key : "class"')
@glrp.rule('type-parameter-key : "typename"')
@cxx98
def type_parameter_key(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-type-parameter : [split:type_parameter]')
@glrp.rule('begin-parameter : [split:parameter]')
@cxx98
def begin_parameter(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('type-constraint : "identifier"[split:type_constraint]')
@glrp.rule(
    'type-constraint : template-name [action:begin_template_list]"<" template-argument-list? "%>"[split:type_constraint]'
)
# TODO: template not allowed
@glrp.rule('type-constraint : nested-name-specifier template? "identifier"[split:type_constraint]')
@glrp.rule(
    'type-constraint : nested-name-specifier template? template-name [action:begin_template_list]"<" template-argument-list? "%>"[split:type_constraint]'
)
@cxx20
def type_constraint_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('template-parameter')
@cxx98_merge
def ambiguous_template_parameter(self, parameter, type_parameter):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser