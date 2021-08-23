"""
namespace-name:
    identifier
    namespace-alias

namespace-definition:
    named-namespace-definition
    unnamed-namespace-definition
    nested-namespace-definition

named-namespace-definition:
    inline? namespace attribute-specifier-seq? identifier { namespace-body }

unnamed-namespace-definition:
    inline? namespace attribute-specifier-seq? { namespace-body }

nested-namespace-definition:
    namespace enclosing-namespace-specifier :: inline? identifier { namespace-body }

enclosing-namespace-specifier:
    identifier
    enclosing-namespace-specifier :: inline? identifier

namespace-body:
    declaration-seq?
"""

import glrp
from ....parser import cxx98, cxx11, cxx17, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('namespace-name[split] : [split]"identifier"')
@glrp.rule('namespace-name : namespace-alias')
@cxx98
def namespace_name(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('namespace-definition : named-namespace-definition')
@glrp.rule('namespace-definition : unnamed-namespace-definition')
@cxx98
def namespace_definition(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('namespace-definition : nested-namespace-definition')
@cxx17
def namespace_definition_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('named-namespace-definition : "namespace" attribute-specifier-seq? "identifier" "{" namespace-body "}"')
@cxx98
def named_namespace_definition(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'named-namespace-definition : "inline" "namespace" attribute-specifier-seq? "identifier" "{" namespace-body "}"'
)
@cxx11
def named_namespace_definition_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('unnamed-namespace-definition : "namespace" attribute-specifier-seq? "{" namespace-body "}"')
@cxx98
def unnamed_namespace_definition(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('unnamed-namespace-definition : "inline" "namespace" attribute-specifier-seq? "{" namespace-body "}"')
@cxx11
def unnamed_namespace_definition_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'nested-namespace-definition : "namespace" enclosing-namespace-specifier "::" "identifier" "{" namespace-body "}"'
)
@cxx17
def nested_namespace_definition_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'nested-namespace-definition : "namespace" enclosing-namespace-specifier "::" "inline" "identifier" "{" namespace-body "}"'
)
@cxx20
def nested_namespace_definition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('enclosing-namespace-specifier : "identifier"')
@glrp.rule('enclosing-namespace-specifier : enclosing-namespace-specifier "::" "identifier"')
@cxx17
def enclosing_namespace_specifier_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('enclosing-namespace-specifier : enclosing-namespace-specifier "::" "inline" "identifier"')
@cxx20
def enclosing_namespace_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('namespace-body : declaration-seq?')
@cxx98
def namespace_body(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser