"""
c++ 98-14:
using-declaration:
    using typename? nested-name-specifier unqualified-id ;
    using :: unqualified-id ;

c++ 17:
using-declaration:
    using using-declarator-list ;

using-declarator-list:
    using-declarator ...?
    using-declarator-list , using-declarator ...?

using-declarator:
    typename? nested-name-specifier unqualified-id
"""

import glrp
from typing import Any, Dict, Tuple
from ...parse import CxxParser, cxx98, cxx17, deprecated_cxx17
from ....ast.declarations import UsingDeclaration
from ....ast.reference import AbstractReference, Reference, TypenameReference, PackExpandReference, TemplateSpecifierId
from ....messages import error, Logger


@error
def invalid_attribute_using_declaration(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an attribute cannot appear before a using declaration"""
    return locals()


@glrp.rule(
    'using-declaration : attribute-specifier-seq? begin-declaration "using" "typename"? nested-name-specifier template? unqualified-id ";"'
)
@cxx98
@deprecated_cxx17
def using_declaration_nested_until_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    # using :: unqualified-id ; is covered here
    if p[0]:
        invalid_attribute_using_declaration(self.logger, p[0][0].position)
    id = p[6]
    if p[5]:
        id = TemplateSpecifierId(p[5].position, id)
    reference = Reference(p[4] + [id])  # type: AbstractReference
    if p[3]:
        reference = TypenameReference(reference)
    return UsingDeclaration([reference])


@glrp.rule('using-declaration : attribute-specifier-seq? begin-declaration "using" using-declarator-list ";"')
@cxx17
def using_declaration_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    if p[0]:
        invalid_attribute_using_declaration(self.logger, p[0][0].position)
    return UsingDeclaration(p[3])


@glrp.rule('using-declarator-list : using-declarator "..."?')
@cxx17
def using_declarator_list_last_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    reference = p[0]
    if p[1]:
        reference = PackExpandReference(reference)
    return [reference]


@glrp.rule('using-declarator-list : using-declarator-list "," using-declarator "..."?')
@cxx17
def using_declarator_list_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    reference = p[2]  # type: AbstractReference
    if p[3]:
        reference = PackExpandReference(reference)
    result.append(reference)
    return result


@glrp.rule('using-declarator : "typename"? nested-name-specifier template? unqualified-id')
@cxx17
def using_declarator_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    id = p[3]
    if p[2]:
        id = TemplateSpecifierId(p[2].position, id)
    reference = Reference(p[1] + [id])  # type: AbstractReference
    if p[0]:
        reference = TypenameReference(reference)
    return reference


@glrp.rule('"typename"? : "typename"')
@cxx98
def typename(self: CxxParser, p: glrp.Production) -> Any:
    return True


@glrp.rule('"typename"? :')
@cxx98
def typename_opt(self: CxxParser, p: glrp.Production) -> Any:
    return False
