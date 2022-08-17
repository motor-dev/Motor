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
from .....parser import cxx20, cxx20_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('requires-expression : requires-disambiguation requires requirement-parameter-list? requirement-body')
@cxx20
def requires_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('requires-disambiguation : ')
@cxx20
def requires_disambiguation_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('requirement-parameter-list? : "(" parameter-declaration-clause ")"')
@glrp.rule('requirement-parameter-list? : ')
@cxx20
def requires_parameter_list_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('requirement-body : "{" requirement-seq "}"')
@cxx20
def requirement_body_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('requirement-seq : requirement')
@glrp.rule('requirement-seq : requirement-seq requirement')
@cxx20
def requirement_seq_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('requirement : simple-requirement')
@glrp.rule('requirement : type-requirement')
@glrp.rule('requirement : compound-requirement')
@glrp.rule('requirement : nested-requirement')
@cxx20
def requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('requirement')
@cxx20_merge
def ambiguous_requirement(self, ambiguous_cast_expression, ambiguous_type_name):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from .....parser import CxxParser
