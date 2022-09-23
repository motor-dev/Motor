"""
deduction-guide:
    explicit-specifier? template-name ( parameter-declaration-clause ) -> simple-template-id ;
"""

import glrp
from ...parser import cxx17
from motor_typing import TYPE_CHECKING


# TODO: attribute-specifier-seq? should be empty
@glrp.rule(
    'deduction-guide : attribute-specifier-seq? begin-decl-deduction-guide explicit-specifier template-name "(" parameter-declaration-clause ")" "->" simple-template-id ";"'
)
@glrp.rule(
    'deduction-guide : attribute-specifier-seq? begin-decl-deduction-guide template-name "(" parameter-declaration-clause ")" "->" simple-template-id ";"'
)
@cxx17
def deduction_guide_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser