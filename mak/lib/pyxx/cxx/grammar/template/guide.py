"""
deduction-guide:
    explicit-specifier? template-name ( parameter-declaration-clause ) -> simple-template-id ;
"""

import glrp
from typing import Any, Dict, Tuple
from ...parse import CxxParser, cxx17
from ....ast.declarations import DeductionGuide, ErrorDeclaration
from ....ast.reference import TemplateId
from ....messages import error, Logger


@error
def invalid_attribute_deduction_guide(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an attribute cannot appear before a deduction guide"""
    return locals()


@glrp.rule(
    'deduction-guide : attribute-specifier-seq? begin-decl-deduction-guide explicit-specifier? "identifier" "(" parameter-declaration-clause ")" "->" template-name "<" template-argument-list? "#>" ";"'
)
@cxx17
def deduction_guide_explicit_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    if p[0]:
        invalid_attribute_deduction_guide(self.logger, p[0][0].position)
    if p[5] is not None:
        return DeductionGuide(p[3], p[2], p[5], TemplateId(p[11].position[1], p[8], p[10]))
    else:
        return ErrorDeclaration()


@glrp.rule(
    'deduction-guide : attribute-specifier-seq? begin-decl-deduction-guide "#error" "(" parameter-declaration-clause ")" "->" template-name "<" template-argument-list? "#>" ";"'
)
@glrp.rule(
    'deduction-guide : attribute-specifier-seq? begin-decl-deduction-guide explicit-specifier? "identifier" "(" parameter-declaration-clause ")" "#error" ";"'
)
@glrp.rule(
    'deduction-guide : attribute-specifier-seq? begin-decl-deduction-guide "#error" "(" parameter-declaration-clause ")" "#error" ";"'
)
@cxx17
def deduction_guide_explicit_error_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorDeclaration()
