"""
new-expression:
    ::? new new-placement? new-type-id new-initializer?
    ::? new new-placement? ( type-id ) new-initializer?

new-placement:
    ( expression-list )

new-type-id:
    type-specifier-seq new-declarator?

new-declarator:
    ptr-operator new-declarator?
    noptr-new-declarator

noptr-new-declarator:
    [ expression? ] attribute-specifier-seq?
    noptr-new-declarator [ constant-expression ] attribute-specifier-seq?

new-initializer:
    ( expression-list? )
    braced-init-list
"""

import glrp
from .....parser import cxx98, cxx11, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('new-expression : "::"? "new" new-type-id new-initializer?')
@glrp.rule('new-expression : "::"? "new" "(" begin-type-id type-id ")" new-initializer?')
@glrp.rule('new-expression : "::"? "new" new-placement new-type-id new-initializer?')
@glrp.rule('new-expression : "::"? "new" new-placement "(" type-id ")" new-initializer?')
@cxx98
def new_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('new-placement : "(" begin-expression expression-list ")"')
@cxx98
def new_placement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('new-type-id : type-specifier-seq')
@glrp.rule('new-type-id : [no-merge-warning]type-specifier-seq new-declarator')
@cxx98
def new_type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('new-declarator : ptr-operator')
@glrp.rule('new-declarator : ptr-operator new-declarator')
@glrp.rule('new-declarator : noptr-new-declarator')
@cxx98
def new_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('noptr-new-declarator : "[" expression? "]" attribute-specifier-seq?')
@glrp.rule('noptr-new-declarator : noptr-new-declarator "[" constant-expression "]" attribute-specifier-seq?')
@cxx98
def noptr_new_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('new-initializer? : "(" expression-list? ")"')
@glrp.rule('new-initializer? : ')
@cxx98
def new_initializer_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('new-initializer? : braced-init-list')
@cxx11
def new_initializer_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('new-type-id-no-declarator')
@cxx98_merge
def ambiguous_new_type_id_no_declarator(self, type_specifier_seq_continue, type_specifier_seq_end):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('new-type-id-declarator')
@cxx98_merge
def ambiguous_new_type_id_declarator(self, type_specifier_seq_continue, type_specifier_seq_end):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('new-expression')
@cxx98_merge
def ambiguous_new_expression(self, type_id, expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('new-type-id')
@cxx98_merge
def ambiguous_new_type_id_constraint(self, id_nontemplate, type_constraint):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from .....parser import CxxParser