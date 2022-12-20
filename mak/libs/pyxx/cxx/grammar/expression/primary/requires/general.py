"""
requires-expression:
    requires requirement-parameter-list? requirement-body

requirement-parameter-list:
    ( parameter-declaration-clause )

requirement-body:
    { requirement-seq }

requirement-seq:
    requirement
    requirement-seq requirement

requirement:
    simple-requirement
    type-requirement
    compound-requirement
    nested-requirement
"""

import glrp
from .....parse import cxx20, cxx20_merge
from ......ast.constraints import RequiresExpression, RequirementBody, AmbiguousRequirement
from motor_typing import TYPE_CHECKING


@glrp.rule('requires-expression : requires requirement-parameter-list? requirement-body')
@cxx20
def requires_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return RequiresExpression(p[1], p[2])


@glrp.rule('requirement-parameter-list? : "(" parameter-declaration-clause ")"')
@cxx20
def requires_parameter_list_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule('requirement-parameter-list? : ')
@cxx20
def requires_parameter_list_empty_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.rule('requirement-body : "{" requirement-seq "}"')
@cxx20
def requirement_body_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return RequirementBody(p[1])


@glrp.rule('requirement-seq : requirement')
@cxx20
def requirement_seq_end_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [p[0]]


@glrp.rule('requirement-seq : requirement-seq requirement')
@cxx20
def requirement_seq_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append(p[1])
    return result


@glrp.rule('requirement : begin-expression simple-requirement')
@cxx20
def requirement_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule('requirement : begin-type-id type-requirement')
@cxx20
def requirement_type_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule('requirement : compound-requirement')
@cxx20
def requirement_compound_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('requirement : nested-requirement')
@cxx20
def requirement_nested_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.merge('requirement')
@cxx20_merge
def ambiguous_requirement(self, type_id, expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousRequirement(type_id + expression)


if TYPE_CHECKING:
    from typing import Any, List
    from .....parse import CxxParser
