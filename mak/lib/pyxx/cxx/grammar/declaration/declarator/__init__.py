"""
init-declarator-list:
    init-declarator
    init-declarator-list , init-declarator

init-declarator:
    declarator initializer?
    declarator requires-clause
"""

import glrp
from typing import Any, List
from ....parse import CxxParser, cxx98, cxx20, cxx98_merge
from .....ast.declarations import AmbiguousInitDeclarator, InitDeclarator

from . import declarator
from . import name
from . import function


@glrp.rule('init-declarator-list : init-declarator')
@cxx98
def init_declarator_list_end(self: CxxParser, p: glrp.Production) -> Any:
    return [[((0, 0), p[0])]]


@glrp.rule('init-declarator-list : init-declarator-list "," init-declarator')
@cxx98
def init_declarator_list(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    for r in result:
        r.append((p[1].position, p[2]))
    return result


@glrp.rule('init-declarator : declarator')
@cxx98
def init_declarator(self: CxxParser, p: glrp.Production) -> Any:
    return InitDeclarator(p[0], None, None)


@glrp.rule('init-declarator : [no-merge-warning]declarator-initializer initializer')
@cxx98
def init_declarator_initializer(self: CxxParser, p: glrp.Production) -> Any:
    return InitDeclarator(p[0], p[1], None)


@glrp.rule('init-declarator : declarator-function-body requires-clause')
@cxx20
def init_declarator_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return InitDeclarator(p[0], None, p[1])


@glrp.merge('init-declarator')
@cxx98_merge
def ambiguous_init_declarator_initializer(
        self: CxxParser, continue_declarator_list: List[Any], end_declarator_list: List[Any]
) -> Any:
    return AmbiguousInitDeclarator(continue_declarator_list + end_declarator_list)


@glrp.merge('init-declarator-list')
@cxx98_merge
def ambiguous_init_declarator_list(
        self: CxxParser, ambiguous_template_argument_list_ellipsis: List[Any], id_template: List[Any],
        ambiguous_initializer_clause: List[Any], ambiguous_init_declarator_list: List[Any], ambiguous_type_id: List[Any]
) -> Any:
    return sum(
        ambiguous_template_argument_list_ellipsis + id_template + ambiguous_initializer_clause +
        ambiguous_init_declarator_list + ambiguous_type_id, []
    )
