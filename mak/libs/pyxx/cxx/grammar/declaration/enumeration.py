"""
enum-name:
    identifier

enum-specifier:
    enum-head { enumerator-list? }
    enum-head { enumerator-list , }

enum-head:
    enum-key attribute-specifier-seq? enum-head-name? enum-base?
    
enum-head-name:
    nested-name-specifier? identifier

opaque-enum-declaration:
    enum-key attribute-specifier-seq? enum-head-name enum-base? ;

enum-key:
    enum
    enum class
    enum struct

enum-base:
    : type-specifier-seq

enumerator-list:
    enumerator-definition
    enumerator-list , enumerator-definition

enumerator-definition:
    enumerator
    enumerator = constant-expression

enumerator:
    identifier attribute-specifier-seq?
"""

import glrp
from ...parse import cxx98, cxx11
from ....ast.enumeration import EnumSpecifier, Enumerator
from ....ast.declarations import OpaqueEnumDeclaration
from ....ast.reference import Reference, Id
from motor_typing import TYPE_CHECKING

#@glrp.rule('enum-name[prec:right,1] : "identifier"')
#@cxx98
#def enum_name(self, p):
#    # type: (CxxParser, glrp.Production) -> Any
#    pass


@glrp.rule('enum-specifier : enum-head "{" enumerator-list? "}"')
@glrp.rule('enum-specifier : enum-head "{" enumerator-list "," "}"')
@cxx98
def enum_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    attributes, enum_is_scoped, name, base = p[0]
    return EnumSpecifier(name, attributes, enum_is_scoped, base, p[2])


@glrp.rule('enum-head : enum-key attribute-specifier-seq? enum-base?')
@cxx98
def enum_head_unnamed(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1], p[0], None, p[2]


@glrp.rule('enum-head : enum-key attribute-specifier-seq? enum-head-name enum-base?')
@cxx98
def enum_head(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1], p[0], p[2], p[3]


@glrp.rule('enum-head-name : "identifier" [split:id_nontemplate]')
@cxx98
def enum_head_name(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference([(False, Id(p[0].value))])


@glrp.rule('enum-head-name : nested-name-specifier template? "identifier"[split:id_nontemplate]')
@cxx98
def enum_head_name_nested(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference(p[0] + [(p[1], Id(p[2].value))])


# TODO: attribute-specifier-seq? empty
@glrp.rule(
    'opaque-enum-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue enum-key attribute-specifier-seq? enum-head-name enum-base? ";"'
)
@cxx11
def opaque_enum_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return OpaqueEnumDeclaration(p[5], p[0], p[4], p[3], p[6])


@glrp.rule('enum-key : "enum"')
@cxx98
def enum_key(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return False


@glrp.rule('enum-key : "enum" "class"')
@glrp.rule('enum-key : "enum" "struct"')
@cxx11
def enum_key_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return True


@glrp.rule('enum-base? : [prec:right,1]')
@cxx98
def enum_base_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.rule('enum-base? : [prec:left,1]":" type-specifier-seq')
@cxx11
def enum_base_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule('enumerator-list : enumerator-definition')
@cxx98
def enumerator_list_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [p[0]]


@glrp.rule('enumerator-list : enumerator-list "," enumerator-definition')
@cxx98
def enumerator_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append(p[2])
    return result


@glrp.rule('enumerator-list? : enumerator-definition')
@cxx98
def enumerator_list_opt_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [p[0]]


@glrp.rule('enumerator-list? : enumerator-list "," enumerator-definition')
@cxx98
def enumerator_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append(p[2])
    return result


@glrp.rule('enumerator-list? : ')
@cxx98
def enumerator_list_opt_empty(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return []


@glrp.rule('enumerator-definition : enumerator')
@cxx98
def enumerator_definition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Enumerator(p[0][0], p[0][1], None)


@glrp.rule('enumerator-definition : enumerator "=" constant-expression')
@cxx98
def enumerator_definition_constant(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Enumerator(p[0][0], p[0][1], p[2])


@glrp.rule('enumerator : identifier attribute-specifier-seq?')
@cxx98
def enumerator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[0].value, p[1])


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser