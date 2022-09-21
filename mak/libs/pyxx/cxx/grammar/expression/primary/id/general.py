"""
id-expression:
    unqualified-id
    qualified-id
"""

import glrp
from .....parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('id-expression : unqualified-id')
@glrp.rule('id-expression : qualified-id')
@cxx98
def id_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('id-expression')
@glrp.merge_result('id_expression')
@cxx98_merge
def id_expression_rename(self, unqualified_id, id_nontemplate, unqualified_id_template, template_name):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any]) -> None
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from .....parser import CxxParser