"""
ctor-initializer:
    : mem-initializer-list

mem-initializer-list:
    mem-initializer ...?
    mem-initializer-list , mem-initializer ...?

mem-initializer:
    mem-initializer-id ( expression-list? )
    mem-initializer-id braced-init-list

mem-initializer-id:
    class-or-decltype
    identifier
"""

import glrp
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx11, cxx98_merge
from ....ast.klass import MemberInitializer, MemInitializerIdMember, MemInitializerIdBase, AmbiguousMemInitializerId, \
    MemberInitializerError
from ....ast.expressions import ParenthesizedExpression, ErrorExpression


@glrp.rule('ctor-initializer : ":" mem-initializer-list')
@glrp.rule('ctor-initializer? : ":" mem-initializer-list')
@cxx98
def ctor_initializer(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('ctor-initializer? : ')
@cxx98
def ctor_initializer_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('mem-initializer-list : mem-initializer')
@cxx98
def mem_initializer_list_end(self: CxxParser, p: glrp.Production) -> Any:
    return [MemberInitializer(p[0][0], p[0][1], False)]


@glrp.rule('mem-initializer-list : mem-initializer-list "," mem-initializer')
@cxx98
def mem_initializer_list(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(MemberInitializer(p[2][0], p[2][1], False))
    return result


@glrp.rule('mem-initializer-list : mem-initializer-list "," "#error"')
@cxx98
def mem_initializer_list_error(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(MemberInitializerError())
    return result


@glrp.rule('mem-initializer-list : mem-initializer "..."')
@cxx11
def mem_initializer_list_pack_end_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return [MemberInitializer(p[0][0], p[0][1], True)]


@glrp.rule('mem-initializer-list : mem-initializer-list "," mem-initializer "..."')
@cxx11
def mem_initializer_list_pack_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(MemberInitializer(p[2][0], p[2][1], True))
    return result


@glrp.rule('mem-initializer : mem-initializer-id "(" expression-list? ")"')
@cxx98
def mem_initializer(self: CxxParser, p: glrp.Production) -> Any:
    return p[0], ParenthesizedExpression(p[2])


@glrp.rule('mem-initializer : mem-initializer-id "(" "#error" ")"')
@cxx98
def mem_initializer_error(self: CxxParser, p: glrp.Production) -> Any:
    return p[0], ErrorExpression()


@glrp.rule('mem-initializer : mem-initializer-id braced-init-list')
@cxx11
def mem_initializer_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0], p[1]


@glrp.rule('mem-initializer-id : class-or-decltype')
@cxx98
def mem_initializer_id_base(self: CxxParser, p: glrp.Production) -> Any:
    return MemInitializerIdBase(p[0])


@glrp.rule('mem-initializer-id[split:mem_initializer] : "identifier"')
@cxx98
def mem_initializer_id(self: CxxParser, p: glrp.Production) -> Any:
    return MemInitializerIdMember(p[0].text())


@glrp.merge('mem-initializer-id')
@cxx98_merge
def ambiguous_mem_initializer_id(self: CxxParser, class_or_decltype: List[Any], mem_initializer: List[Any]) -> Any:
    return AmbiguousMemInitializerId(mem_initializer + class_or_decltype)
