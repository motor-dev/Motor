"""
simple-template-id:
    template-name < template-argument-list? >

template-id:
    simple-template-id
    operator-function-id < template-argument-list? >
    literal-operator-id < template-argument-list? >

template-name:
    identifier

template-argument-list:
    template-argument ...?
    template-argument-list , template-argument ...?

template-argument:
    constant-expression
    type-id
    id-expression

typename-specifier:
    typename nested-name-specifier identifier
    typename nested-name-specifier template? simple-template-id
"""

import glrp
from ...parser import cxx98, cxx11, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('template? : "template"')
@glrp.rule('template? : ')
@cxx98
def template_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('simple-template-id : template-name [prec:left,1][action:split_rightshift]"<" template-argument-list? ">"')
@cxx98
def simple_template_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-id[prec:right,1][split:template_id] : simple-template-id')
@glrp.rule(
    'template-id : operator-function-id [split:template_operator][action:split_rightshift]"<" template-argument-list? ">"'
)
@cxx98
def template_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'template-id : literal-operator-id [split:template_literal][action:split_rightshift]"<" template-argument-list? ">"'
)
@cxx11
def template_id_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-name[prec:right,1][split:template_name] : "identifier"')
@cxx98
def template_name(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-argument-list? : template-argument')
@glrp.rule('template-argument-list? : template-argument-list "," template-argument')
@glrp.rule('template-argument-list? : ')
@cxx98
def template_argument_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-argument-list? : template-argument "..."')
@glrp.rule('template-argument-list? : template-argument-list "," template-argument "..."')
@cxx11
def template_argument_list_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-argument-list : template-argument')
@glrp.rule('template-argument-list : template-argument-list "," template-argument')
@cxx98
def template_argument_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-argument-list : template-argument "..."')
@glrp.rule('template-argument-list : template-argument-list "," template-argument "..."')
@cxx11
def template_argument_list_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-argument : template-argument-proxy')
@cxx98
def template_argument(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-argument-proxy : constant-expression')
@glrp.rule('template-argument-proxy : type-id')
@glrp.rule('template-argument-proxy : id-expression')
@cxx98
def template_argument_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('template-argument-proxy')
@cxx98_merge
def ambiguous_template_argument_proxy(self, ambiguous_cast_expression, ambiguous_type_id, id_expression):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('template-argument-proxy')
@cxx98_merge
def ambiguous_template_argument_proxy_literal(self, ambiguous_relational_expression_literal, template_literal):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('template-argument-proxy')
@cxx98_merge
def ambiguous_template_argument_proxy_operator(self, ambiguous_relational_expression_operator, template_operator):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


# TODO: template not allowed
@glrp.rule('typename-specifier : "typename" typename-disambiguation nested-name-specifier "template"? "identifier"')
@glrp.rule(
    'typename-specifier : "typename" typename-disambiguation nested-name-specifier "template"? simple-template-id'
)
@cxx98
def typename_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('typename-disambiguation[split:typename_specifier] :')
@cxx98
def typename_disambiguation(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ...parser import CxxParser