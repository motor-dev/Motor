"""
deduction-guide:
    explicit-specifier? template-name ( parameter-declaration-clause ) -> simple-template-id ;
"""

import glrp
from ...parser import cxx17
from motor_typing import TYPE_CHECKING


# TODO: attribute-specifier-seq? should be empty
@glrp.rule(
    'deduction-guide : attribute-specifier-seq? deduction-guide-begin explicit-specifier template-name "(" parameter-declaration-clause ")" "->" simple-template-id ";"'
)
@glrp.rule(
    'deduction-guide : attribute-specifier-seq? template-name[split:deduction_guide] "(" parameter-declaration-clause ")" "->" simple-template-id ";"'
)
@cxx17
def deduction_guide_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('deduction-guide-begin[split:explicit_deduction] :')
@cxx17
def deduction_guide_begin_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser