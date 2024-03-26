"""
linkage-specification:
    extern string-literal { declaration-seq? }
    extern string-literal declaration
"""

import glrp
from typing import Any, Dict, Tuple
from ...parse import CxxParser, cxx98
from ....ast.declarations import LinkageSpecification
from ....messages import error, Logger


@error
def invalid_attribute_linkage_specification(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an attribute cannot appear before a linkage specification"""
    return locals()


@glrp.rule(
    'linkage-specification : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" "string-literal" "{" declaration-seq? "}"'
)
@cxx98
def linkage_specification_seq(self: CxxParser, p: glrp.Production) -> Any:
    if p[0]:
        invalid_attribute_linkage_specification(self.logger, p[0][0].position)
    return LinkageSpecification(p[4].value, p[6])


@glrp.rule(
    'linkage-specification : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" "string-literal" declaration'
)
@cxx98
def linkage_specification(self: CxxParser, p: glrp.Production) -> Any:
    if p[0]:
        invalid_attribute_linkage_specification(self.logger, p[0][0].position)
    return LinkageSpecification(p[4].value, [p[5]])
