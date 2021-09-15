"""
deduction-guide:
    explicit-specifier? template-name ( parameter-declaration-clause ) -> simple-template-id ;
"""

import glrp
from ...parser import cxx17
from motor_typing import TYPE_CHECKING


#@glrp.rule('deduction-guide : template-name "(" parameter-declaration-clause ")" "->" simple-template-id ";"')
@glrp.rule(
    'deduction-guide : attribute-specifier-seq? template-name [split]"(" parameter-declaration-clause ")" "->" simple-template-id ";"'
)
@cxx17
def deduction_guide_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser