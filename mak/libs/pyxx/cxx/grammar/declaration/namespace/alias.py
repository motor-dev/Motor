"""
namespace-alias:
    identifier

namespace-alias-definition:
    namespace identifier = qualified-namespace-specifier ;

qualified-namespace-specifier:
    nested-name-specifier? namespace-name
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('namespace-alias[prec:right,1] : "identifier"')
@cxx98
def namespace_alias(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


# TODO: attribute-specifier-seq? -> empty
@glrp.rule(
    'namespace-alias-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? "identifier" "=" qualified-namespace-specifier ";"'
)
@cxx98
def namespace_alias_definition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('qualified-namespace-specifier : namespace-name')
@glrp.rule('qualified-namespace-specifier : nested-name-specifier template? namespace-name')
@cxx98
def qualified_namespace_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser