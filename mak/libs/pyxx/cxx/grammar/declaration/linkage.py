"""
linkage-specification:
    extern string-literal { declaration-seq? }
    extern string-literal declaration
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx98
from ....ast.declarations import LinkageSpecification


# TODO: attribute-specifier-seq? not allowed
@glrp.rule(
    'linkage-specification : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" "string-literal" "{" declaration-seq? "}"'
)
@cxx98
def linkage_specification_seq(self: CxxParser, p: glrp.Production) -> Any:
    return LinkageSpecification(p[0], p[4].value, p[6])


@glrp.rule(
    'linkage-specification : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" "string-literal" declaration'
)
@cxx98
def linkage_specification(self: CxxParser, p: glrp.Production) -> Any:
    return LinkageSpecification(p[0], p[4].value, [p[5]])
