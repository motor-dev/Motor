"""
namespace-alias:
    identifier

s:
    namespace identifier = qualified-namespace-specifier ;

qualified-namespace-specifier:
    nested-name-specifier? namespace-name
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.declarations import NamespaceAliasDeclaration
from .....ast.reference import Reference, TemplateSpecifierId

#@glrp.rule('namespace-alias : "identifier"')
#@cxx98
#def namespace_alias(self: CxxParser, p: glrp.Production) -> Any:
#    # type: (CxxParser, glrp.Production) -> Any
#    pass


# TODO: attribute-specifier-seq? -> empty
@glrp.rule(
    'namespace-alias-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? "identifier" "=" qualified-namespace-specifier ";"'
)
@cxx98
def namespace_alias_definition(self: CxxParser, p: glrp.Production) -> Any:
    return NamespaceAliasDeclaration(p[0], p[3], p[4].value, p[6])


@glrp.rule('qualified-namespace-specifier : namespace-name')
@cxx98
def qualified_namespace_specifier(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([p[0]])


@glrp.rule('qualified-namespace-specifier : nested-name-specifier template? namespace-name')
@cxx98
def qualified_namespace_specifier_nested(self: CxxParser, p: glrp.Production) -> Any:
    id = p[2]
    if p[1]:
        id = TemplateSpecifierId(id)
    return Reference(p[0] + [id])
