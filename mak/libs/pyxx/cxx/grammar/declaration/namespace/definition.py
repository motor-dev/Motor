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
from .....ast.declarations import NamespaceDeclaration
from motor_typing import TYPE_CHECKING


@glrp.rule('namespace-name : "identifier"')
#lass-head-name@glrp.rule('namespace-name : namespace-alias')
@cxx98
def namespace_name(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0].value


@glrp.rule('namespace-definition : named-namespace-definition')
@glrp.rule('namespace-definition : unnamed-namespace-definition')
@cxx98
def namespace_definition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('namespace-definition : nested-namespace-definition')
@cxx17
def namespace_definition_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'named-namespace-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? "identifier" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx98
def named_namespace_definition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NamespaceDeclaration(p[0], p[3], p[5], False, None, p[4].value, p[7])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'named-namespace-definition : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "inline" "namespace" attribute-specifier-seq? "identifier" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx11
def named_namespace_definition_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NamespaceDeclaration(p[0], p[5], p[7], True, None, p[6].value, p[9])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'unnamed-namespace-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx98
def unnamed_namespace_definition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NamespaceDeclaration(p[0], p[3], None, False, None, None, p[5])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'unnamed-namespace-definition : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "inline" "namespace" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx11
def unnamed_namespace_definition_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NamespaceDeclaration(p[0], p[5], None, True, None, None, p[7])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'nested-namespace-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? enclosing-namespace-specifier "::" "identifier" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx17
def nested_namespace_definition_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NamespaceDeclaration(p[0], p[3], p[7], False, p[4], p[6].value, p[9])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'nested-namespace-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? enclosing-namespace-specifier "::" "inline" "identifier" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx20
def nested_namespace_definition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NamespaceDeclaration(p[0], p[3], p[8], True, p[4], p[7].value, p[10])


@glrp.rule('enclosing-namespace-specifier : "identifier"')
@cxx17
def enclosing_namespace_specifier_end_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [(False, p[0].value)]


@glrp.rule('enclosing-namespace-specifier : enclosing-namespace-specifier "::" "identifier"')
@cxx17
def enclosing_namespace_specifier_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0] + [(False, p[2].value)]


@glrp.rule('enclosing-namespace-specifier : enclosing-namespace-specifier "::" "inline" "identifier"')
@cxx20
def enclosing_namespace_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0] + [(True, p[3].value)]


@glrp.rule('namespace-body : declaration-seq?')
@cxx98
def namespace_body(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser