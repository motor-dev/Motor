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
from .....parser import cxx98, cxx11
from ......ast.reference import Id, TemplateId, DestructorId
from motor_typing import TYPE_CHECKING


@glrp.rule('unqualified-id : "identifier" [split:id_nontemplate]')
@cxx98
def unqualified_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Id(p[0].value)


@glrp.rule('unqualified-id : operator-function-id[split:id_nontemplate]')
@cxx98
def unqualified_operator_function_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('unqualified-id : conversion-function-id')
@cxx98
def unqualified_conversion_function_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('unqualified-id : "~" destructor-disambiguation "identifier" [split:id_nontemplate]')
@cxx98
def unqualified_destructor_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DestructorId(Id(p[2].value))


@glrp.rule('unqualified-id : "~" destructor-disambiguation template-name "<" template-argument-list? "#>"')
@cxx98
def unqualified_destructor_template_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DestructorId(TemplateId(p[2], p[4]))


@glrp.rule('unqualified-id : template-id')
@cxx98
def unqualified_template_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('unqualified-id : literal-operator-id[split:id_nontemplate]')
@cxx11
def unqualified_literal_operator_id_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('unqualified-id : "~" destructor-disambiguation decltype-specifier')
@cxx11
def unqualified_destructor_decltype_id_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DestructorId(p[2])


@glrp.rule('destructor-disambiguation :')
@cxx98
def destructor_disambiguation(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser