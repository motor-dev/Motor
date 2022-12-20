"""
using-directive:
    attribute-specifier-seq? using namespace nested-name-specifier? namespace-name ;
"""

import glrp
from ....parse import cxx98
from .....ast.declarations import UsingDirective
from .....ast.reference import Reference, Id
from motor_typing import TYPE_CHECKING


@glrp.rule('using-directive : attribute-specifier-seq? begin-declaration "using" "namespace" namespace-name ";"')
@cxx98
def using_directive(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return UsingDirective(p[0], Reference([(False, Id(p[4]))]))


@glrp.rule(
    'using-directive : attribute-specifier-seq? begin-declaration "using" "namespace" nested-name-specifier template? namespace-name ";"'
)
@cxx98
def using_directive_nested(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return UsingDirective(p[0], Reference(p[4] + [(p[5], Id(p[6]))]))


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser