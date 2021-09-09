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
from .....parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('requires-expression : requires requirement-parameter-list? requirement-body')
@cxx20
def requires_expression_cxx20(self, p):
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


if TYPE_CHECKING:
    from .....parser import CxxParser
