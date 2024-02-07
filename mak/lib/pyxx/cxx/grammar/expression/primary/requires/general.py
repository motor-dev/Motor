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
from typing import Any, List
from .....parse import CxxParser, cxx20, cxx20_merge
from ......ast.constraints import RequiresExpression, RequirementBody, AmbiguousRequirement
from ......ast.expressions import ErrorExpression


@glrp.rule('constant-expression : requires requirement-parameter-list? requirement-body')
@glrp.rule('constant-expression# : requires requirement-parameter-list? requirement-body')
@glrp.rule('constraint-logical-expression : requires requirement-parameter-list? requirement-body')
@cxx20
def requires_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    if p[1] is not None and p[2] is not None:
        return RequiresExpression(p[1], p[2])
    else:
        return ErrorExpression()


@glrp.rule('requirement-parameter-list? : "(" parameter-declaration-clause ")"')
@cxx20
def requires_parameter_list_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('requirement-parameter-list? : "(" "#error" ")"')
@cxx20
def requires_parameter_list_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('requirement-parameter-list? : ')
@cxx20
def requires_parameter_list_empty_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('requirement-body : "{" requirement-seq "}"')
@cxx20
def requirement_body_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return RequirementBody(p[1])


@glrp.rule('requirement-body : "{" begin-expression "#error" "}"')
@cxx20
def requirement_body_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('requirement-seq : requirement')
@cxx20
def requirement_seq_end_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]]


@glrp.rule('requirement-seq : requirement-seq requirement')
@cxx20
def requirement_seq_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(p[1])
    return result


@glrp.rule('requirement : begin-expression simple-requirement')
@cxx20
def requirement_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('requirement : begin-type-id type-requirement')
@cxx20
def requirement_type_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('requirement : compound-requirement')
@cxx20
def requirement_compound_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('requirement : nested-requirement')
@cxx20
def requirement_nested_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.merge('requirement')
@cxx20_merge
def ambiguous_requirement(self: CxxParser, type_id: List[Any], expression: List[Any]) -> Any:
    return AmbiguousRequirement(type_id + expression)
