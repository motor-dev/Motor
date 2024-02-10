"""
unqualified-id:
    identifier
    operator-function-id
    conversion-function-id
    literal-operator-id
    ~ type-name
    ~ decltype-specifier
    template-id
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx98, cxx11, cxx20
from ......ast.reference import Id, TemplateId, DestructorId


@glrp.rule('"identifier" : "%identifier"')
@cxx98
def identifier(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('"identifier" : [prec:nonassoc,0][split:continue_declarator_list]"final"')
@glrp.rule('"identifier" : [prec:nonassoc,0][split:continue_declarator_list]"override"')
@cxx11
def identifier_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('unqualified-id : "identifier" [split:id_nontemplate]')
@cxx98
def unqualified_id(self: CxxParser, p: glrp.Production) -> Any:
    return Id(p[0].position, p[0].value)


@glrp.rule('constraint-unqualified-id : "identifier" [split:id_nontemplate]')
@cxx20
def unqualified_id_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return Id(p[0].position, p[0].value)


@glrp.rule('unqualified-id : operator-function-id[split:id_nontemplate]')
@cxx98
def unqualified_operator_function_id(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('unqualified-id : conversion-function-id')
@cxx98
def unqualified_conversion_function_id(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('unqualified-id : "~" destructor-disambiguation "identifier" [split:id_nontemplate]')
@cxx98
def unqualified_destructor_id(self: CxxParser, p: glrp.Production) -> Any:
    return DestructorId(p[0].position, Id(p[2].position, p[2].value))


@glrp.rule('unqualified-id : "~" destructor-disambiguation template-name "<" template-argument-list? "#>"')
@cxx98
def unqualified_destructor_template_id(self: CxxParser, p: glrp.Production) -> Any:
    return DestructorId(p[0].position, TemplateId(p[5].position[1], p[2], p[4]))


@glrp.rule('unqualified-id : template-id')
@cxx98
def unqualified_template_id(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('constraint-unqualified-id : template-id')
@cxx20
def unqualified_template_id_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('unqualified-id : literal-operator-id[split:id_nontemplate]')
@cxx11
def unqualified_literal_operator_id_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('unqualified-id : "~" destructor-disambiguation decltype-specifier')
@cxx98
def unqualified_destructor_decltype_id_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return DestructorId(p[0].position, p[2])


@glrp.rule('destructor-disambiguation :')
@cxx98
def destructor_disambiguation(self: CxxParser, p: glrp.Production) -> Any:
    pass
