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
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx11, cxx98_merge
from ....ast.reference import Id, TemplateId, Reference, TypenameReference, TemplateSpecifierId, _Id
from ....ast.type import TypeSpecifierReference
from ....ast.template import AmbiguousTemplateArgument, TemplateArgumentPackExpand, TemplateArgumentConstant, TemplateArgumentTypeId


@glrp.rule('template? : "template"')
@cxx98
def template_opt(self: CxxParser, p: glrp.Production) -> Any:
    return True


@glrp.rule('template? : ')
@cxx98
def template_empty_opt(self: CxxParser, p: glrp.Production) -> Any:
    return False


#@glrp.rule(
#    'simple-template-id : template-name "<" template-argument-list? "#>"'
#)
#@cxx98
#def simple_template_id(self: CxxParser, p: glrp.Production) -> Any:
#    # type: (CxxParser, glrp.Production) -> Any
#    pass


@glrp.rule('template-id : template-name "<" template-argument-list? "#>" [split:id_nontemplate]')
@glrp.rule('template-id : operator-function-id [split:id_template]"<" template-argument-list? "#>"')
@cxx98
def template_id(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateId(p[0], p[2])


@glrp.rule('template-id : literal-operator-id [split:id_template]"<" template-argument-list? "#>"')
@cxx11
def template_literal_id(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateId(p[0], p[2])


@glrp.rule('template-name : "identifier" [split:id_template]')
@cxx98
def template_name(self: CxxParser, p: glrp.Production) -> Any:
    return Id(p[0].value)


@glrp.rule('template-argument-list? : template-argument-list')
@cxx98
def template_argument_list_opt(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('template-argument-list? : ')
@cxx98
def template_argument_list_empty_opt(self: CxxParser, p: glrp.Production) -> Any:
    return []


@glrp.rule('template-argument-list : template-argument')
@cxx98
def template_argument_list_end(self: CxxParser, p: glrp.Production) -> Any:
    return [[p[0]]]


@glrp.rule('template-argument-list : template-argument-list "," template-argument')
@cxx98
def template_argument_list(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    for r in result:
        r.append(p[2])
    return result


@glrp.rule('template-argument-list : "#error"')
@cxx98
def template_argument_list_error_end(self: CxxParser, p: glrp.Production) -> Any:
    return [[p[0]]]


@glrp.rule('template-argument-list : template-argument-list "," "#error"')
@cxx98
def template_argument_list_error(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    for r in result:
        r.append(p[2])
    return result


@glrp.rule('template-argument-list : [no-merge-warning] template-argument "..."')
@cxx11
def template_argument_list_pack_end_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return [[TemplateArgumentPackExpand(p[0])]]


@glrp.rule('template-argument-list : template-argument-list "," [no-merge-warning] template-argument "..."')
@cxx11
def template_argument_list_pack_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    for r in result:
        r.append(TemplateArgumentPackExpand(p[2]))
    return result


@glrp.rule('template-argument : begin-template-argument-constant "constant-expression#"')
@cxx98
def template_argument_constant(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateArgumentConstant(p[1])


@glrp.rule('template-argument : begin-template-argument-type type-id')
#@glrp.rule('template-argument : id-expression')
@cxx98
def template_argument(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateArgumentTypeId(p[1])


# TODO: template not allowed
@glrp.rule('typename-specifier : "typename" nested-name-specifier "template"? "identifier" [split:id_nontemplate]')
@cxx98
def typename_specifier(self: CxxParser, p: glrp.Production) -> Any:
    id = Id(p[3].value)    # type: _Id
    if p[2]:
        id = TemplateSpecifierId(id)
    return TypeSpecifierReference(TypenameReference(Reference(p[1] + [id])))


@glrp.rule(
    'typename-specifier : "typename" nested-name-specifier "template"? template-name "<" template-argument-list? "#>"'
)
@cxx98
def typename_specifier_template(self: CxxParser, p: glrp.Production) -> Any:
    id = TemplateId(p[3], p[5])    # type: _Id
    if p[2]:
        id = TemplateSpecifierId(id)
    return TypeSpecifierReference(TypenameReference(Reference(p[1] + [id])))


@glrp.rule('begin-template-argument-constant[split:template_argument_constant] :')
@glrp.rule('begin-template-argument-type[split:template_argument_type] :')
@cxx98
def begin_template_argument(self: CxxParser, p: glrp.Production) -> Any:
    pass


@glrp.merge('template-argument')
@cxx98_merge
def ambiguous_template_argument(
    self: CxxParser, template_argument_constant: List[Any], template_argument_type: List[Any]
) -> Any:
    return AmbiguousTemplateArgument(template_argument_constant + template_argument_type)


@glrp.merge('template-argument-list')
@cxx98_merge
def ambiguous_template_argument_list_ellipsis(
    self: CxxParser, ambiguous_template_argument: List[Any], ambiguous_template_argument_list_ellipsis: List[Any],
    end_declarator_list: List[Any], continue_declarator_list: List[Any], ambiguous_expression: List[Any]
) -> Any:
    return sum(
        ambiguous_template_argument + ambiguous_template_argument_list_ellipsis + end_declarator_list +
        continue_declarator_list + ambiguous_expression, []
    )
