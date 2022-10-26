"""
namespace-alias:
    identifier

s:
    namespace identifier = qualified-namespace-specifier ;

qualified-namespace-specifier:
    nested-name-specifier? namespace-name
"""

import glrp
from ....parser import cxx98
from .....ast.declarations import NamespaceAliasDeclaration
from .....ast.reference import Reference, Id
from motor_typing import TYPE_CHECKING

#@glrp.rule('namespace-alias : "identifier"')
#@cxx98
#def namespace_alias(self, p):
#    # type: (CxxParser, glrp.Production) -> Any
#    pass


# TODO: attribute-specifier-seq? -> empty
@glrp.rule(
    'namespace-alias-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? "identifier" "=" qualified-namespace-specifier ";"'
)
@cxx98
def namespace_alias_definition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NamespaceAliasDeclaration(p[0], p[3], p[4].value, p[6])


@glrp.rule('qualified-namespace-specifier : namespace-name')
@cxx98
def qualified_namespace_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference([(False, p[0])])


@glrp.rule('qualified-namespace-specifier : nested-name-specifier template? namespace-name')
@cxx98
def qualified_namespace_specifier_nested(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference(p[0] + [(p[1], Id(p[2]))])


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser