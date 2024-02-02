"""
decl-specifier:
    storage-class-specifier
    defining-type-specifier
    function-specifier
    friend
    typedef
    constexpr
    consteval
    constinit
    inline

decl-specifier-seq:
    decl-specifier attribute-specifier-seq?
    decl-specifier decl-specifier-seq
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx11, cxx20
from .....ast.declarations import DeclSpecifierSeq, DeclarationSpecifierMacro, DeclarationSpecifiers
from typing import TYPE_CHECKING
from . import storage
from . import function
from . import typedef
from . import type


@glrp.rule('decl-specifier : defining-type-specifier-1')
@glrp.rule('decl-specifier : defining-type-specifier-2')
@cxx98
def decl_specifier_defining_type_specifier(self: CxxParser, p: glrp.Production) -> Any:
    return (None, p[0])


@glrp.rule('decl-specifier : function-specifier')
@cxx98
def decl_specifier_function_specifier(self: CxxParser, p: glrp.Production) -> Any:
    return (p[0], None)


@glrp.rule('decl-specifier : storage-class-specifier')
@cxx98
def decl_specifier_storage_class_specifier(self: CxxParser, p: glrp.Production) -> Any:
    return (p[0], None)


@glrp.rule('decl-specifier : "friend"')
@glrp.rule('decl-specifier : "friend" [prec:left,0]"attribute-specifier-macro"')
@glrp.rule('decl-specifier : "friend" [prec:left,0]"attribute-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def decl_specifier_friend(self: CxxParser, p: glrp.Production) -> Any:
    return (DeclarationSpecifiers.FRIEND, None)


@glrp.rule('decl-specifier : "typedef"')
@cxx98
def decl_specifier_typedef(self: CxxParser, p: glrp.Production) -> Any:
    return (DeclarationSpecifiers.TYPEDEF, None)


@glrp.rule('decl-specifier : "inline"')
@cxx98
def decl_specifier_inline(self: CxxParser, p: glrp.Production) -> Any:
    return (DeclarationSpecifiers.INLINE, None)


@glrp.rule('decl-specifier : "decl-specifier-macro"')
@cxx98
def decl_specifier_macro(self: CxxParser, p: glrp.Production) -> Any:
    return (DeclarationSpecifierMacro(p[0].value, None), None)


@glrp.rule('decl-specifier : "decl-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def decl_specifier_macro_function(self: CxxParser, p: glrp.Production) -> Any:
    return (DeclarationSpecifierMacro(p[0].value, p[2]), None)


@glrp.rule('decl-specifier : "constexpr"')
@cxx11
def decl_specifier_constexpr_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return (DeclarationSpecifiers.CONSTEXPR, None)


@glrp.rule('decl-specifier : "consteval"')
@cxx20
def decl_specifier_consteval_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return (DeclarationSpecifiers.CONSTEVAL, None)


@glrp.rule('decl-specifier : "constinit"')
@cxx20
def decl_specifier_constinit_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return (DeclarationSpecifiers.CONSTINIT, None)


@glrp.rule('decl-specifier-seq-head : decl-specifier-seq-head decl-specifier-seq-continue decl-specifier')
@cxx98
def decl_specifier_seq_head_ctn(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0][:]
    result.append(p[2])
    return result


@glrp.rule('decl-specifier-seq-head : decl-specifier-seq-continue decl-specifier')
@cxx98
def decl_specifier_seq_head(self: CxxParser, p: glrp.Production) -> Any:
    result = []
    result.append(p[1])
    return result


@glrp.rule('decl-specifier-seq : decl-specifier-seq-head decl-specifier-seq-end attribute-specifier-seq?')
@glrp.rule('decl-specifier-seq? : decl-specifier-seq-head decl-specifier-seq-end attribute-specifier-seq?')
@cxx98
def decl_specifier_seq(self: CxxParser, p: glrp.Production) -> Any:
    result = DeclSpecifierSeq(p[2])
    for decl_specifier in p[0]:
        if decl_specifier[0] is not None:
            result.add_decl_specifier(decl_specifier[0])
        else:
            result.add_type_specifier(decl_specifier[1])
    return result


@glrp.rule('decl-specifier-seq? : decl-specifier-seq-end attribute-specifier-seq?')
@cxx98
def decl_specifier_seq_end(self: CxxParser, p: glrp.Production) -> Any:
    return DeclSpecifierSeq(p[1])


@glrp.rule('decl-specifier-seq-end : [split:decl_specifier_seq_end]')
@glrp.rule('decl-specifier-seq-continue : [split:decl_specifier_seq_continue]')
@cxx98
def decl_specifier_seq_end_continue(self: CxxParser, p: glrp.Production) -> Any:
    pass
