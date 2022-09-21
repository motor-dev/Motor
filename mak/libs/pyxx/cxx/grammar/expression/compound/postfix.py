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
@glrp.rule('postfix-expression : simple-type-specifier "(" expression-list? ")"')
@glrp.rule('postfix-expression : typename-specifier"(" expression-list? ")"')
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
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('postfix-expression : simple-type-specifier braced-init-list')
@glrp.rule('postfix-expression : typename-specifier braced-init-list')
@cxx11
def postfix_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('typeid-expression : typeid "(" begin-expression expression ")"')
@glrp.rule('typeid-expression : typeid "(" begin-type-id type-id ")"')
@cxx98
def typeid_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('expression-list? : expression-list')
@glrp.rule('expression-list? :')
@cxx98
def expression_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('expression-list : initializer-list')
@cxx98
def expression_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-type-id : [split:type_id]')
@glrp.rule('begin-expression : [split:expression]')
@cxx98
def begin_type_or_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('typeid-expression')
@cxx98_merge
def ambiguous_typeid_expression(self, type_id, expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser