from . import primary
from . import compound
from . import constant

from motor_typing import TYPE_CHECKING
import glrp
from ...parse import cxx98_merge
from ....ast.expressions import AmbiguousExpression


@glrp.merge('primary-expression-proxy')
@glrp.merge('constraint-expression')
@glrp.merge('relational-expression')
@glrp.merge('relational-expression#')
@glrp.merge('expression-proxy')
@glrp.merge('constant-expression#')
@glrp.merge('constant-expression')
@glrp.merge('shift-expression')
@glrp.merge('shift-expression#')
@glrp.merge('fold-expression')
@glrp.merge('typeid-expression')
@glrp.merge('postfix-expression')
@glrp.merge('sizeof-expression')
@glrp.merge('new-expression')
@glrp.merge('cast-expression')
@glrp.merge('additive-expression')
@glrp.merge('multiplicative-expression')
@glrp.merge('equality-expression')
@glrp.merge('equality-expression#')
@glrp.merge('and-expression')
@glrp.merge('and-expression#')
@glrp.merge('exclusive-or-expression')
@glrp.merge('exclusive-or-expression#')
@glrp.merge('inclusive-or-expression')
@glrp.merge('inclusive-or-expression#')
@glrp.merge('logical-and-expression')
@glrp.merge('logical-and-expression#')
@glrp.merge('logical-or-expression')
@glrp.merge('logical-or-expression#')
@glrp.merge('conditional-expression')
@glrp.merge('conditional-expression#')
@glrp.merge('assignment-expression')
@glrp.merge('assignment-expression#')
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