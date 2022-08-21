"""
postfix-expression:
    primary-expression
    postfix-expression [ expr-or-braced-init-list ]
    postfix-expression ( expression-list? )
    simple-type-specifier ( expression-list? )
    typename-specifier ( expression-list? )
    simple-type-specifier braced-init-list
    typename-specifier braced-init-list
    postfix-expression . template? id-expression
    postfix-expression -> template? id-expression
    postfix-expression ++
    postfix-expression --
    dynamic_cast < type-id > ( expression )
    static_cast < type-id > ( expression )
    reinterpret_cast < type-id > ( expression )
    const_cast < type-id > ( expression )
    typeid ( expression )
    typeid ( type-id )

expression-list:
    initializer-list
"""

import glrp
from ....parser import cxx98, cxx11, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('postfix-expression : primary-expression')
@glrp.rule('postfix-expression : postfix-expression "[" expr-or-braced-init-list "]"')
@glrp.rule('postfix-expression : postfix-expression "(" expression-list? ")"')
@glrp.rule('postfix-expression : simple-type-specifier [split:ambiguous_cast_expression]"(" expression-list? ")"')
@glrp.rule('postfix-expression : typename-specifier [split:ambiguous_cast_expression]"(" expression-list? ")"')
@glrp.rule('postfix-expression : postfix-expression "." template? id-expression')
@glrp.rule('postfix-expression : postfix-expression "->" template? id-expression')
@glrp.rule('postfix-expression : postfix-expression "++"')
@glrp.rule('postfix-expression : postfix-expression "--"')
@glrp.rule('postfix-expression : "dynamic_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : "static_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : "reinterpret_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : "const_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : typeid-expression')
@cxx98
def postfix_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('postfix-expression : simple-type-specifier braced-init-list')
@glrp.rule('postfix-expression : typename-specifier braced-init-list')
@cxx11
def postfix_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('typeid-expression : typeid "(" expression ")"')
@glrp.rule('typeid-expression : typeid "(" type-id ")"')
@cxx98
def typeid_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('expression-list? : expression-list')
@glrp.rule('expression-list? :')
@cxx98
def expression_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('expression-list : initializer-list')
@cxx98
def expression_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('typeid-expression')
@cxx98_merge
def ambiguous_typeid_expression(self, ambiguous_type_id, ambiguous_cast_expression):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    # typeid (type-id) vs typeid(expression)
    pass


@glrp.merge('postfix-expression')
@cxx98_merge
def generic_postfix_expression(
    self, ambiguous_type_id, id_expression, ambiguous_simple_type_specifier, ambiguous_nested_name_specifier
):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ....parser import CxxParser