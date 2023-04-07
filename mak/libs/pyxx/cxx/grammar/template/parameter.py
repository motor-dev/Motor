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
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx11, cxx20, cxx98_merge
from ....ast.template import AmbiguousTemplateParameter, TemplateParameterType, TemplateParameterTemplate, TemplateParameterConstant, TemplateParameterConstraint
from ....ast.reference import Reference, Id, TemplateId, TemplateSpecifierId, _Id


@glrp.rule('template-parameter : begin-type-parameter type-parameter')
@cxx98
def template_parameter_type(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('template-parameter : begin-parameter "parameter-declaration#"')
@cxx98
def template_parameter_constant(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateParameterConstant(p[1])


# amendment: @glrp.rule('type-parameter : type-parameter-key "identifier"?')
# amendment: @glrp.rule('type-parameter : type-parameter-key "identifier"? "=" type-id')
# amendment: @glrp.rule('type-parameter : template-head type-parameter-key "identifier"?')
# amendment: @glrp.rule('type-parameter : template-head type-parameter-key "identifier"? "=" id-expression')
@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "identifier"?')
@cxx98
def type_parameter_type(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return TemplateParameterType(p[1], p[2], None, False)


@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "identifier"? "=" type-id')
@cxx98
def type_parameter_type_default(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return TemplateParameterType(p[1], p[2], p[4], False)


@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "identifier"?')
@cxx98
def type_parameter_template(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return TemplateParameterTemplate(p[2], p[1][0], p[1][1], p[3], None, False)


@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "identifier"? "=" id-expression')
@cxx98
def type_parameter_template_default(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return TemplateParameterTemplate(p[2], p[1][0], p[1][1], p[3], p[5], False)


# amendment: @glrp.rule('type-parameter : type-parameter-key "..." "identifier"?')
# amendment: @glrp.rule('type-parameter : template-head type-parameter-key "..." "identifier"?')
@glrp.rule('type-parameter : attribute-specifier-seq? type-parameter-key "..." "identifier"?')
@cxx11
def type_parameter_type_pack_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return TemplateParameterType(p[1], p[3], None, True)


@glrp.rule('type-parameter : attribute-specifier-seq? template-head type-parameter-key "..." "identifier"?')
@cxx11
def type_parameter_template_pack_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return TemplateParameterTemplate(p[2], p[1][0], p[1][1], p[4], None, True)


# amendment: @glrp.rule('type-parameter : type-constraint "identifier"?')
# amendment: @glrp.rule('type-parameter : type-constraint "..." "identifier"?')
# amendment: @glrp.rule('type-parameter : type-constraint "identifier"? "=" type-id')
@glrp.rule('type-parameter : attribute-specifier-seq? type-constraint "identifier"?')
@cxx20
def type_parameter_constraint_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return TemplateParameterConstraint(p[1], p[2], None, False)


@glrp.rule('type-parameter : attribute-specifier-seq? type-constraint "..." "identifier"?')
@cxx20
def type_parameter_constraint_pack_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return TemplateParameterConstraint(p[1], p[3], None, True)


@glrp.rule('type-parameter : attribute-specifier-seq? type-constraint "identifier"? "=" type-id')
@cxx20
def type_parameter_constraint_default_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return TemplateParameterConstraint(p[1], p[2], p[4], False)


@glrp.rule('type-parameter-key : "class"')
@glrp.rule('type-parameter-key : "typename"')
@cxx98
def type_parameter_key(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].text()


@glrp.rule('begin-type-parameter : [split:type_parameter]')
@glrp.rule('begin-parameter : [split:parameter]')
@cxx98
def begin_parameter(self: CxxParser, p: glrp.Production) -> Any:
    pass


@glrp.rule('type-constraint : "identifier"')
@cxx20
def type_constraint_identifier_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([Id(p[0].value)])


@glrp.rule('type-constraint : template-name "<" template-argument-list? "#>"')
@cxx20
def type_constraint_template_name_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([TemplateId(p[0], p[2])])


# TODO: template not allowed
@glrp.rule('type-constraint : nested-name-specifier template? "identifier"')
@cxx20
def type_constraint_nested_identifier_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    id = Id(p[2].value)    # type: _Id
    if p[1]:
        id = TemplateSpecifierId(id)
    return Reference(p[0] + [id])


@glrp.rule('type-constraint : nested-name-specifier template? template-name "<" template-argument-list? "#>"')
@cxx20
def type_constraint_nested_template_id_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    id = TemplateId(p[2], p[4])    # type: _Id
    if p[1]:
        id = TemplateSpecifierId(id)
    return Reference(p[0] + [id])


@glrp.merge('template-parameter')
@cxx98_merge
def ambiguous_template_parameter(self: CxxParser, parameter: List[Any], type_parameter: List[Any]) -> Any:
    return AmbiguousTemplateParameter(parameter + type_parameter)
