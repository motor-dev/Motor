"""
relational-expression:
    compare-expression
    relational-expression < compare-expression
    relational-expression > compare-expression
    relational-expression <= compare-expression
    relational-expression >= compare-expression
"""

import glrp
from ....parser import cxx98, cxx98_merge
from .....ast.expressions import BinaryExpression, AmbiguousExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('relational-expression : compare-expression')
@glrp.rule('"relational-expression#" : "compare-expression#"')
@cxx98
def relational_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('relational-expression : [no-merge-warning] relational-expression "<" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression ">" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression "<=" compare-expression')
@glrp.rule('relational-expression : [no-merge-warning] relational-expression ">=" compare-expression')
@glrp.rule('"relational-expression#" : [no-merge-warning] "relational-expression#" "<" "compare-expression#"')
@glrp.rule('"relational-expression#" : [no-merge-warning] "relational-expression#" "<=" "compare-expression#"')
@glrp.rule('"relational-expression#" : [no-merge-warning] "relational-expression#" ">=" "compare-expression#"')
@cxx98
def relational_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.merge('relational-expression')
@cxx98_merge
def ambiguous_relational_expression(
    self, ambiguous_relational_expression, ambiguous_shift_expression, ambiguous_template_id, id_template,
    id_nontemplate, ambiguous_template_argument_list_ellipsis
):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any], List[Any], List[Any]) -> Any
    all_exprs = ambiguous_relational_expression + ambiguous_shift_expression + ambiguous_template_id + id_template + id_nontemplate + ambiguous_template_argument_list_ellipsis
    return AmbiguousExpression(all_exprs)


@glrp.merge('relational-expression#')
@glrp.merge_result('ambiguous_relational_expression')
@cxx98_merge
def ambiguous_relational_expression_ext(
    self, ambiguous_relational_expression, ambiguous_shift_expression, ambiguous_template_id, id_template,
    id_nontemplate, ambiguous_template_argument_list_ellipsis
):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any], List[Any], List[Any]) -> Any
    all_exprs = ambiguous_relational_expression + ambiguous_shift_expression + ambiguous_template_id + id_template + id_nontemplate + ambiguous_template_argument_list_ellipsis
    return AmbiguousExpression(all_exprs)


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser