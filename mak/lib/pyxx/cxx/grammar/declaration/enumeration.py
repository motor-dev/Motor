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
from typing import Any
from ...parse import CxxParser, cxx98, cxx11
from ....ast.enumeration import EnumSpecifier, Enumerator
from ....ast.type import ErrorTypeSpecifier
from ....ast.declarations import OpaqueEnumDeclaration, ErrorDeclaration
from ....ast.reference import Reference, Id, TemplateSpecifierId, _Id


# @glrp.rule('enum-name[prec:right,1] : "identifier"')
# @cxx98
# def enum_name(self: CxxParser, p: glrp.Production) -> Any:
#    # type: (CxxParser, glrp.Production) -> Any
#    pass


@glrp.rule('enum-specifier : enum-head "{" enumerator-list? "}"')
@glrp.rule('enum-specifier : enum-head "{" enumerator-list "," "}"')
@cxx98
def enum_specifier(self: CxxParser, p: glrp.Production) -> Any:
    position, attributes, enum_is_scoped, name, base = p[0]
    if name is not None:
        position = (position[0], name.position[1])
    return EnumSpecifier(position, name, attributes, enum_is_scoped, base, p[2])


@glrp.rule('enum-specifier : enum-key #error "{" enumerator-list? "}"')
@glrp.rule('enum-specifier : enum-key #error "{" enumerator-list "," "}"')
@cxx98
def enum_specifier_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorTypeSpecifier(p[1].position)


@glrp.rule('enum-head : enum-key attribute-specifier-seq? enum-base?')
@cxx98
def enum_head_unnamed(self: CxxParser, p: glrp.Production) -> Any:
    return p[0][0], p[1], p[0][1], None, p[2]


@glrp.rule('enum-head : enum-key attribute-specifier-seq? enum-head-name enum-base?')
@cxx98
def enum_head(self: CxxParser, p: glrp.Production) -> Any:
    return p[0][0], p[1], p[0][1], p[2], p[3]


@glrp.rule('enum-head-name : "identifier" [split:id_nontemplate]')
@cxx98
def enum_head_name(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([Id(p[0].position, p[0].value)])


@glrp.rule('enum-head-name : nested-name-specifier template? "identifier"[split:id_nontemplate]')
@cxx98
def enum_head_name_nested(self: CxxParser, p: glrp.Production) -> Any:
    id = Id(p[2].position, p[2].value)  # type: _Id
    if p[1]:
        id = TemplateSpecifierId(p[1].position, id)
    return Reference(p[0] + [id])


# TODO: attribute-specifier-seq? empty
@glrp.rule(
    'opaque-enum-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue enum-key attribute-specifier-seq? enum-head-name enum-base? ";"'
)
@cxx11
def opaque_enum_declaration_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return OpaqueEnumDeclaration(p[5], p[0], p[4], p[3], p[6])


@glrp.rule(
    'opaque-enum-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue enum-key "#error" ";"'
)
@cxx11
def opaque_enum_declaration_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorDeclaration()


@glrp.rule('enum-key : "enum"')
@cxx98
def enum_key(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].position, False


@glrp.rule('enum-key : "enum" "class"')
@glrp.rule('enum-key : "enum" "struct"')
@cxx11
def enum_key_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return (p[0].position[0], p[1].position[1]), True


@glrp.rule('enum-base? : [prec:right,1]')
@cxx98
def enum_base_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('enum-base? : [prec:left,1]":" type-specifier-seq')
@cxx11
def enum_base_opt_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('enumerator-list : enumerator-definition')
@cxx98
def enumerator_list_end(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]]


@glrp.rule('enumerator-list : enumerator-list "," enumerator-definition')
@cxx98
def enumerator_list(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(p[2])
    return result


@glrp.rule('enumerator-list? : enumerator-definition')
@cxx98
def enumerator_list_opt_end(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]]


@glrp.rule('enumerator-list? : enumerator-list "," enumerator-definition')
@cxx98
def enumerator_list_opt(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(p[2])
    return result


@glrp.rule('enumerator-list? : ')
@cxx98
def enumerator_list_opt_empty(self: CxxParser, p: glrp.Production) -> Any:
    return []


@glrp.rule('enumerator-definition : enumerator')
@cxx98
def enumerator_definition(self: CxxParser, p: glrp.Production) -> Any:
    return Enumerator(p[0][0], p[0][1], None)


@glrp.rule('enumerator-definition : enumerator "=" constant-expression')
@cxx98
def enumerator_definition_constant(self: CxxParser, p: glrp.Production) -> Any:
    return Enumerator(p[0][0], p[0][1], p[2])


@glrp.rule('enumerator : identifier attribute-specifier-seq?')
@cxx98
def enumerator(self: CxxParser, p: glrp.Production) -> Any:
    return (p[0].value, p[1])
