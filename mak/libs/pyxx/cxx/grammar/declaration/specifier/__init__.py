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
from ....parse import cxx98, cxx11, cxx20
from .....ast.declarations import DeclSpecifierSeq, DeclarationSpecifierMacro, DeclarationSpecifiers
from motor_typing import TYPE_CHECKING
from . import storage
from . import function
from . import typedef
from . import type


@glrp.rule('decl-specifier : defining-type-specifier-1')
@glrp.rule('decl-specifier : defining-type-specifier-2')
@cxx98
def decl_specifier_defining_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (None, p[0])


@glrp.rule('decl-specifier : function-specifier')
@cxx98
def decl_specifier_function_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[0], None)


@glrp.rule('decl-specifier : storage-class-specifier')
@cxx98
def decl_specifier_storage_class_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[0], None)


@glrp.rule('decl-specifier : "friend"')
@cxx98
def decl_specifier_friend(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (DeclarationSpecifiers.FRIEND, None)


@glrp.rule('decl-specifier : "typedef"')
@cxx98
def decl_specifier_typedef(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (DeclarationSpecifiers.TYPEDEF, None)


@glrp.rule('decl-specifier : "inline"')
@cxx98
def decl_specifier_inline(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (DeclarationSpecifiers.INLINE, None)


@glrp.rule('decl-specifier : "decl-specifier-macro"')
@cxx98
def decl_specifier_macro(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (DeclarationSpecifierMacro(p[0].value, None), None)


@glrp.rule('decl-specifier : "decl-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def decl_specifier_macro_function(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (DeclarationSpecifierMacro(p[0].value, p[2]), None)


@glrp.rule('decl-specifier : "constexpr"')
@cxx11
def decl_specifier_constexpr_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (DeclarationSpecifiers.CONSTEXPR, None)


@glrp.rule('decl-specifier : "consteval"')
@cxx20
def decl_specifier_consteval_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (DeclarationSpecifiers.CONSTEVAL, None)


@glrp.rule('decl-specifier : "constinit"')
@cxx20
def decl_specifier_constinit_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (DeclarationSpecifiers.CONSTINIT, None)


@glrp.rule('decl-specifier-seq : decl-specifier-seq-continue decl-specifier decl-specifier-seq?')
@glrp.rule('decl-specifier-seq? : decl-specifier-seq-continue decl-specifier decl-specifier-seq?')
@cxx98
def decl_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[2]
    if p[1][0] is not None:
        result.add_decl_specifier(p[1][0])
    else:
        result.add_type_specifier(p[1][1])
    return result


@glrp.rule('decl-specifier-seq? : decl-specifier-seq-end attribute-specifier-seq?')
@cxx98
def decl_specifier_seq_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = DeclSpecifierSeq(p[1])
    return result


@glrp.rule('decl-specifier-seq-end : [split:decl_specifier_seq_end]')
@glrp.rule('decl-specifier-seq-continue : [split:decl_specifier_seq_continue]')
@cxx98
def decl_specifier_seq_end_continue(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser