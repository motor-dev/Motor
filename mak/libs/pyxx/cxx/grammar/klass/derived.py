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
from ...parser import cxx98, cxx11, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('base-clause? : [prec:left,1]":" base-specifier-list')
@glrp.rule('base-clause? : ')
@cxx98
def base_clause_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('base-specifier-list : base-specifier "..."?')
@glrp.rule('base-specifier-list : base-specifier-list "," base-specifier "..."?')
@cxx98
def base_specifier_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('base-specifier : attribute-specifier-seq? class-or-decltype')
@glrp.rule('base-specifier : attribute-specifier-seq? virtual access-specifier? class-or-decltype')
@glrp.rule('base-specifier : attribute-specifier-seq? access-specifier virtual? class-or-decltype')
@cxx98
def base_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('class-or-decltype[split:class_or_decltype] : "identifier"')
@glrp.rule('class-or-decltype : template-name "<" template-argument-list? "#>"')
@glrp.rule('class-or-decltype : nested-name-specifier template? identifier')
@glrp.rule('class-or-decltype : nested-name-specifier template? template-name "<" template-argument-list? "#>"')
# TODO: already covered above
#@glrp.rule('class-or-decltype : nested-name-specifier template? simple-template-id')
@cxx98
def class_or_decltype(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('class-or-decltype : decltype-specifier')
@cxx11
def class_or_decltype_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('access-specifier : "private"')
@glrp.rule('access-specifier : "protected"')
@glrp.rule('access-specifier : "public"')
@glrp.rule('access-specifier : "access-specifier-macro"')
@glrp.rule('access-specifier : "access-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def access_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('access-specifier? : "private"')
@glrp.rule('access-specifier? : "protected"')
@glrp.rule('access-specifier? : "public"')
@glrp.rule('access-specifier? : "access-specifier-macro"')
@glrp.rule('access-specifier? : "access-specifier-macro-function" "(" balanced-token-seq? ")"')
@glrp.rule('access-specifier? : ')
@cxx98
def access_specifier_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('virtual? : "virtual"')
@glrp.rule('virtual? : ')
@cxx98
def virtual_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('base-specifier-list')
@cxx98_merge
def ambiguous_base_specifier_list(self, ambiguous_base_specifier_list, ambiguous_template_argument_list_ellipsis):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser