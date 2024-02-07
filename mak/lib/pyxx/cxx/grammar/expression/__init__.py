from . import primary
from . import compound
from . import constant

from typing import TYPE_CHECKING
import glrp
from ...parse import cxx98_merge
from ....ast.expressions import AmbiguousExpression


@glrp.merge('expression')
@glrp.merge('constant-expression')
@glrp.merge('constant-expression#')
@cxx98_merge
def ambiguous_expression(
        self, ambiguous_expression, id_template, id_nontemplate, ambiguous_template_argument_list_ellipsis, expression,
        fold_expression, type_id, simple_type_specifier_cast, ambiguous_initializer_clause
):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any], List[Any], List[Any], List[Any], List[Any], List[Any]) -> Any
    return AmbiguousExpression(
        ambiguous_expression + id_template + id_nontemplate + ambiguous_template_argument_list_ellipsis + expression +
        fold_expression + type_id + simple_type_specifier_cast + ambiguous_initializer_clause
    )


if TYPE_CHECKING:
    from typing import Any, List
    from ...parse import CxxParser
