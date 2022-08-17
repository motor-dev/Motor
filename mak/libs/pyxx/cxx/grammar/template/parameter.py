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


@glrp.rule('template-parameter : type-parameter')
@glrp.rule('template-parameter : parameter-declaration')
@cxx98
def template_parameter(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('template-parameter')
@cxx98_merge
def ambiguous_template_parameter(self, ambiguous_type_constraint, ambiguous_decl_specifier_seq):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('template-parameter')
@cxx98_merge
def ambiguous_template_parameter_2(self, type_parameter, defining_type_specifier):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('template-parameter')
@cxx98_merge
def ambiguous_template_parameter_3(self, typename_parameter, typename_specifier):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
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
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? not allowed
    pass


# amendment: @glrp.rule('type-parameter : type-parameter-key "..." "identifier"?')
# amendment: @glrp.rule('type-parameter : template-head type-parameter-key "..." "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "..." "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "..." "identifier"?')
@cxx11
def type_parameter_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
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
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? not allowed
    pass


@glrp.rule('type-parameter-key : type-parameter-disambiguation "class"')
@glrp.rule('type-parameter-key[split:typename_parameter] : "typename"')
@cxx98
def type_parameter_key(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-parameter-disambiguation[split:type_parameter] :')
@cxx98
def type_parameter_disambiguation(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-constraint : concept-name')
@glrp.rule('type-constraint : concept-name [action:split_rightshift]"<" template-argument-list? ">"')
# TODO: template not allowed
@glrp.rule('type-constraint : nested-name-specifier template? concept-name')
@glrp.rule(
    'type-constraint : nested-name-specifier template? concept-name [action:split_rightshift]"<" template-argument-list? ">"'
)
@cxx20
def type_constraint_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('type-constraint')
@cxx20_merge
def ambiguous_type_constraint(self, template_name, concept_name, ambiguous_nested_name_specifier):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ...parser import CxxParser