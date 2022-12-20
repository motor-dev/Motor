"""
init-declarator-list:
    init-declarator
    init-declarator-list , init-declarator

init-declarator:
    declarator initializer?
    declarator requires-clause
"""

import glrp
from ....parse import cxx98, cxx20, cxx98_merge
from .....ast.declarations import AmbiguousInitDeclarator, InitDeclarator, InitDeclaratorList, AmbiguousInitDeclaratorList
from motor_typing import TYPE_CHECKING
from . import declarator
from . import name
from . import function


@glrp.rule('init-declarator-list : init-declarator')
@cxx98
def init_declarator_list_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return InitDeclaratorList(p[0])


@glrp.rule('init-declarator-list : init-declarator-list "," init-declarator')
@cxx98
def init_declarator_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0].add(p[2])


@glrp.rule('init-declarator : declarator')
@cxx98
def init_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return InitDeclarator(p[0], None, None)


@glrp.rule('init-declarator : [no-merge-warning]declarator-initializer initializer')
@cxx98
def init_declarator_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return InitDeclarator(p[0], p[1], None)


@glrp.rule('init-declarator : declarator-function-body requires-clause')
@cxx20
def init_declarator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return InitDeclarator(p[0], None, p[1])


@glrp.merge('init-declarator')
@cxx98_merge
def ambiguous_init_declarator_initializer(self, continue_declarator_list, end_declarator_list):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousInitDeclarator(continue_declarator_list + end_declarator_list)


@glrp.merge('init-declarator-list')
@cxx98_merge
def ambiguous_init_declarator_list(
    self, ambiguous_template_argument_list_ellipsis, id_template, ambiguous_initializer_clause,
    ambiguous_init_declarator_list, ambiguous_type_id
):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any], List[Any]) -> Any
    return AmbiguousInitDeclaratorList(
        ambiguous_template_argument_list_ellipsis + id_template + ambiguous_initializer_clause +
        ambiguous_init_declarator_list + ambiguous_type_id
    )


if TYPE_CHECKING:
    from typing import Any, List
    from ....parse import CxxParser