"""
using-directive:
    attribute-specifier-seq? using namespace nested-name-specifier? namespace-name ;
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.declarations import UsingDirective
from .....ast.reference import Reference, TemplateSpecifierId, _Id


@glrp.rule('using-directive : attribute-specifier-seq? begin-declaration "using" "namespace" namespace-name ";"')
@cxx98
def using_directive(self: CxxParser, p: glrp.Production) -> Any:
    return UsingDirective(p[0], Reference([p[4]]))


@glrp.rule(
    'using-directive : attribute-specifier-seq? begin-declaration "using" "namespace" nested-name-specifier template? namespace-name ";"'
)
@cxx98
def using_directive_nested(self: CxxParser, p: glrp.Production) -> Any:
    id = p[6]  # type: _Id
    if p[5]:
        id = TemplateSpecifierId(p[5].position, id)
    return UsingDirective(p[0], Reference(p[4] + [id]))
