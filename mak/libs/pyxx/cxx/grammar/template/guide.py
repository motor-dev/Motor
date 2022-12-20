"""
deduction-guide:
    explicit-specifier? template-name ( parameter-declaration-clause ) -> simple-template-id ;
"""

import glrp
from ...parse import cxx17
from ....ast.declarations import DeductionGuide
from ....ast.reference import TemplateId
from motor_typing import TYPE_CHECKING


# TODO: attribute-specifier-seq? should be empty
@glrp.rule(
    'deduction-guide : attribute-specifier-seq? begin-decl-deduction-guide explicit-specifier? "identifier" "(" parameter-declaration-clause ")" "->" template-name "<" template-argument-list? "#>" ";"'
)
@cxx17
def deduction_guide_explicit_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DeductionGuide(p[0], p[3], p[2], p[5], TemplateId(p[8], p[10]))


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser