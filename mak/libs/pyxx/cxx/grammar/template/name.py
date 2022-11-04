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
from ....ast.reference import Id, TemplateId, Reference
from ....ast.types import TypeSpecifierReference
from motor_typing import TYPE_CHECKING


@glrp.rule('template? : "template"')
@cxx98
def template_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return True


@glrp.rule('template? : ')
@cxx98
def template_empty_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return False


#@glrp.rule(
#    'simple-template-id : template-name "<" template-argument-list? "#>"'
#)
#@cxx98
#def simple_template_id(self, p):
#    # type: (CxxParser, glrp.Production) -> Any
#    pass


@glrp.rule('template-id : template-name "<" template-argument-list? "#>" [split:id_nontemplate]')
@glrp.rule('template-id : operator-function-id [split:id_template]"<" template-argument-list? "#>"')
@cxx98
def template_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TemplateId(p[0], p[2])


@glrp.rule('template-id : literal-operator-id [split:id_template]"<" template-argument-list? "#>"')
@cxx11
def template_literal_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TemplateId(p[0], p[2])


@glrp.rule('template-name : "identifier" [split:id_template]')
@cxx98
def template_name(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Id(p[0].value)


@glrp.rule('template-argument-list? : template-argument-list')
@cxx98
def template_argument_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('template-argument-list? : ')
@cxx98
def template_argument_list_empty_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return []


@glrp.rule('template-argument-list : template-argument')
@cxx98
def template_argument_list_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [p[0]]


@glrp.rule('template-argument-list : template-argument-list "," template-argument')
@cxx98
def template_argument_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    #result.append(p[2])
    return result


@glrp.rule('template-argument-list : [no-merge-warning] template-argument "..."')
@glrp.rule('template-argument-list : template-argument-list "," [no-merge-warning] template-argument "..."')
@cxx11
def template_argument_list_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('template-argument : begin-template-argument-constant "constant-expression#"')
@glrp.rule('template-argument : begin-template-argument-type type-id')
#@glrp.rule('template-argument : id-expression')
@cxx98
def template_argument(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


# TODO: template not allowed
@glrp.rule('typename-specifier : "typename" nested-name-specifier "template"? "identifier" [split:id_nontemplate]')
@cxx98
def typename_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeSpecifierReference(Reference(p[1] + [(p[2], Id(p[3].value))]), True)


@glrp.rule(
    'typename-specifier : "typename" nested-name-specifier "template"? template-name "<" template-argument-list? "#>"'
)
@cxx98
def typename_specifier_template(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeSpecifierReference(Reference(p[1] + [(p[2], TemplateId(p[3], p[5]))]), True)


@glrp.rule('begin-template-argument-constant[split:template_argument_constant] :')
@glrp.rule('begin-template-argument-type[split:template_argument_type] :')
@cxx98
def begin_template_argument(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('template-argument')
@cxx98_merge
def ambiguous_template_argument(self, template_argument_constant, template_argument_type):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('template-argument-list')
@cxx98_merge
def ambiguous_template_argument_list_ellipsis(
    self, ambiguous_template_argument, ambiguous_template_argument_list_ellipsis, end_declarator_list,
    continue_declarator_list, ambiguous_constant_expression
):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any], List[Any]) -> Any
    pass


@glrp.merge('template-id')
@cxx98_merge
def ambiguous_template_id(self, id_template, ambiguous_template_argument_list_ellipsis):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser