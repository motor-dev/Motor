"""
conversion-function-id:
    operator conversion-type-id

conversion-type-id:
    type-specifier-seq conversion-declarator?

conversion-declarator:
    ptr-operator conversion-declarator?
"""

import glrp
from ...parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('conversion-function-id : operator conversion-type-id')
@cxx98
def conversion_function_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('conversion-type-id : conversion-type-id-declarator')
@glrp.rule('conversion-type-id : conversion-type-id-no-declarator')
@glrp.rule('conversion-type-id-no-declarator : begin-type-id-no-declarator type-specifier-seq')
@glrp.rule(
    'conversion-type-id-declarator : begin-type-id-declarator [no-merge-warning] type-specifier-seq conversion-declarator'
)
@cxx98
def conversion_type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('conversion-declarator : ptr-operator conversion-declarator?')
@cxx98
def conversion_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('conversion-declarator? : ptr-operator conversion-declarator?')
@glrp.rule('conversion-declarator? : ')
@cxx98
def conversion_declarator_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('conversion-type-id-declarator')
@cxx98_merge
def ambiguous_conversion_type_id_declarator(self, type_specifier_seq_end, type_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('conversion-type-id')
@cxx98_merge
def ambiguous_conversion_type_id(self, type_id_declarator, type_id_no_declarator):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser