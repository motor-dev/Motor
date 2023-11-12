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
from typing import Any
from ....parse import CxxParser, cxx98, cxx11, cxx17, cxx20
from .....ast.declarations import NamespaceDeclaration, ErrorDeclaration
from .....ast.reference import Id


@glrp.rule('namespace-name : "identifier"')
# @glrp.rule('namespace-name : namespace-alias')
@cxx98
def namespace_name(self: CxxParser, p: glrp.Production) -> Any:
    return Id(p[0].position, p[0].value)


@glrp.rule('namespace-definition : named-namespace-definition')
@glrp.rule('namespace-definition : unnamed-namespace-definition')
@cxx98
def namespace_definition(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('namespace-definition : nested-namespace-definition')
@cxx17
def namespace_definition_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule(
    'named-namespace-definition : attribute-specifier-seq? begin-declaration "namespace" "#error" "{" namespace-body "}"'
)
@cxx98
def error_namespace_definition(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorDeclaration()


@glrp.rule(
    'named-namespace-definition : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "inline" "namespace" "#error" "{" namespace-body "}"'
)
@cxx11
def error_namespace_definition_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorDeclaration()


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'named-namespace-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? "identifier" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx98
def named_namespace_definition(self: CxxParser, p: glrp.Production) -> Any:
    position = p[2].position[0], p[4].position[1]
    return NamespaceDeclaration(position, p[0], p[3], p[5], False, [], p[4].value, p[7])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'named-namespace-definition : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "inline" "namespace" attribute-specifier-seq? "identifier" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx11
def named_namespace_definition_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    position = p[3].position[0], p[6].position[1]
    return NamespaceDeclaration(position, p[0], p[5], p[7], True, [], p[6].value, p[9])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'unnamed-namespace-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx98
def unnamed_namespace_definition(self: CxxParser, p: glrp.Production) -> Any:
    position = p[2].position
    return NamespaceDeclaration(position, p[0], p[3], [], False, [], None, p[5])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'unnamed-namespace-definition : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "inline" "namespace" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx11
def unnamed_namespace_definition_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    position = p[3].position[0], p[4].position[1]
    return NamespaceDeclaration(position, p[0], p[5], [], True, [], None, p[7])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'nested-namespace-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? enclosing-namespace-specifier "::" "identifier" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx17
def nested_namespace_definition_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    position = p[2].position[0], p[6].position[1]
    return NamespaceDeclaration(position, p[0], p[3], p[7], False, p[4], p[6].value, p[9])


# amendment: attribute-specifier-seq? to simplify grammar.
@glrp.rule(
    'nested-namespace-definition : attribute-specifier-seq? begin-declaration "namespace" attribute-specifier-seq? enclosing-namespace-specifier "::" "inline" "identifier" attribute-specifier-seq? "{" namespace-body "}"'
)
@cxx20
def nested_namespace_definition_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    position = p[2].position[0], p[7].position[1]
    return NamespaceDeclaration(position, p[0], p[3], p[8], True, p[4], p[7].value, p[10])


@glrp.rule('enclosing-namespace-specifier : "identifier"')
@cxx17
def enclosing_namespace_specifier_end_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return [(False, p[0].value)]


@glrp.rule('enclosing-namespace-specifier : enclosing-namespace-specifier "::" "identifier"')
@cxx17
def enclosing_namespace_specifier_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return p[0] + [(False, p[2].value)]


@glrp.rule('enclosing-namespace-specifier : enclosing-namespace-specifier "::" "inline" "identifier"')
@cxx20
def enclosing_namespace_specifier_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0] + [(True, p[3].value)]


@glrp.rule('namespace-body : declaration-seq?')
@cxx98
def namespace_body(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]
