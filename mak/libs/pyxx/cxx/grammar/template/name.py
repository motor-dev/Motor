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
from ...parser import cxx98, cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('template? : "template"')
@glrp.rule('template? : ')
@cxx98
def template_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('simple-template-id : template-name [split]"<" template-argument-list? ">"')
@cxx98
def simple_template_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-id[split] : simple-template-id')
@glrp.rule('template-id : operator-function-id[split] "<" template-argument-list? ">"')
@cxx98
def template_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-id : literal-operator-id[split] "<" template-argument-list? ">"')
@cxx11
def template_id_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-name[split:template_identifier] : [split]"identifier"')
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


@glrp.rule('template-argument : constant-expression')
@glrp.rule('template-argument : type-id')
@glrp.rule('template-argument : id-expression[prec:right,0]')
@cxx98
def template_argument(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


# TODO: template not allowed
@glrp.rule('typename-specifier[split] : [prec:left,1]"typename" nested-name-specifier "template"? "identifier"')
@glrp.rule('typename-specifier : [prec:left,1]"typename" nested-name-specifier "template"? simple-template-id')
@cxx98
def typename_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser