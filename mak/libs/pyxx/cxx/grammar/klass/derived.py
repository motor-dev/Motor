"""
base-clause:
    : base-specifier-list

base-specifier-list:
    base-specifier ...?
    base-specifier-list , base-specifier ...?

base-specifier:
    attribute-specifier-seq? class-or-decltype
    attribute-specifier-seq? virtual access-specifier? class-or-decltype
    attribute-specifier-seq? access-specifier virtual? class-or-decltype

class-or-decltype:
    nested-name-specifier? type-name
    nested-name-specifier template simple-template-id
    decltype-specifier

access-specifier:
    private
    protected
    public
"""

import glrp
from ...parse import cxx98, cxx11, cxx98_merge
from ....ast.klass import BaseSpecifier, AccessSpecifierDefault, AccessSpecifierPublic, AccessSpecifierProtected, AccessSpecifierPrivate, AccessSpecifierMacro
from ....ast.reference import TemplateId, Id, Reference
from ....ast.type import PrimitiveTypeSpecifiers, TypeSpecifierReference, AmbiguousTypeSpecifier
from motor_typing import TYPE_CHECKING


@glrp.rule('base-clause? : [prec:left,1]":" base-specifier-list')
@cxx98
def base_clause(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule('base-clause? : ')
@cxx98
def base_clause_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [[]]


@glrp.rule('base-specifier-list : base-specifier "..."?')
@cxx98
def base_specifier_list_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [[BaseSpecifier(p[0][0], p[0][1], p[0][2], p[0][3], p[1])]]


@glrp.rule('base-specifier-list : base-specifier-list "," base-specifier "..."?')
@cxx98
def base_specifier_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    for r in result:
        r.append(BaseSpecifier(p[2][0], p[2][1], p[2][2], p[2][3], p[3]))
    return result


@glrp.rule('base-specifier : attribute-specifier-seq? class-or-decltype')
@cxx98
def base_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[1], p[0], AccessSpecifierDefault(), False)


@glrp.rule('base-specifier : attribute-specifier-seq? virtual access-specifier? class-or-decltype')
@cxx98
def base_specifier_virtual(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[3], p[0], p[2], True)


@glrp.rule('base-specifier : attribute-specifier-seq? access-specifier virtual? class-or-decltype')
@cxx98
def base_specifier_access_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[3], p[0], p[1], p[2])


@glrp.rule('class-or-decltype[split:class_or_decltype] : "identifier"')
@cxx98
def class_or_decltype(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeSpecifierReference(Reference([(False, Id(p[0].value))]), False)


@glrp.rule('class-or-decltype : template-name "<" template-argument-list? "#>"')
@cxx98
def class_or_decltype_template(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeSpecifierReference(Reference([(False, TemplateId(p[0], p[2]))]), False)


@glrp.rule('class-or-decltype : nested-name-specifier template? identifier')
@cxx98
def class_or_decltype_nested(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeSpecifierReference(Reference(p[0] + [(p[1], Id(p[2].value))]), False)


@glrp.rule('class-or-decltype : nested-name-specifier template? template-name "<" template-argument-list? "#>"')
# TODO: already covered above
#@glrp.rule('class-or-decltype : nested-name-specifier template? simple-template-id')
@cxx98
def class_or_decltype_nested_template(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeSpecifierReference(Reference(p[0] + [(p[1], TemplateId(p[2], p[4]))]), False)


@glrp.rule('class-or-decltype : decltype-specifier')
@cxx11
def class_or_decltype_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('access-specifier : "private"')
@glrp.rule('access-specifier? : "private"')
@cxx98
def access_specifier_private(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AccessSpecifierPrivate()


@glrp.rule('access-specifier : "protected"')
@glrp.rule('access-specifier? : "protected"')
@cxx98
def access_specifier_protected(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AccessSpecifierProtected()


@glrp.rule('access-specifier : "public"')
@glrp.rule('access-specifier? : "public"')
@cxx98
def access_specifier_public(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AccessSpecifierPublic()


@glrp.rule('access-specifier : "access-specifier-macro"')
@glrp.rule('access-specifier? : "access-specifier-macro"')
@cxx98
def access_specifier_macro(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AccessSpecifierMacro(p[0].text(), None)


@glrp.rule('access-specifier : "access-specifier-macro-function" "(" balanced-token-seq? ")"')
@glrp.rule('access-specifier? : "access-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def access_specifier_macro_arguments(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AccessSpecifierMacro(p[0].text(), p[2])


@glrp.rule('access-specifier? : ')
@cxx98
def access_specifier_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AccessSpecifierDefault()


@glrp.rule('virtual? : "virtual"')
@cxx98
def virtual(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return True


@glrp.rule('virtual? : ')
@cxx98
def virtual_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return False


@glrp.merge('base-specifier-list')
@cxx98_merge
def ambiguous_base_specifier_list(self, ambiguous_base_specifier_list, ambiguous_template_argument_list_ellipsis):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return sum(ambiguous_base_specifier_list + ambiguous_template_argument_list_ellipsis, [])


if TYPE_CHECKING:
    from typing import Any, List
    from ...parse import CxxParser