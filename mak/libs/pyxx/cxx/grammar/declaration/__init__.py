"""
declaration-seq:
    declaration
    declaration-seq declaration

declaration:
    block-declaration
    nodeclspec-function-declaration
    function-definition
    template-declaration
    deduction-guide
    explicit-instantiation
    explicit-specialization
    export-declaration
    linkage-specification
    namespace-definition
    empty-declaration
    attribute-declaration
    module-import-declaration

block-declaration:
    simple-declaration
    asm-declaration
    namespace-alias-definition
    using-declaration
    using-enum-declaration
    using-directive
    static_assert-declaration
    alias-declaration
    opaque-enum-declaration

nodeclspec-function-declaration:
    attribute-specifier-seq? declarator ;

alias-declaration:
    using identifier attribute-specifier-seq? = defining-type-id ;

simple-declaration:
    decl-specifier-seq init-declarator-list? ;
    attribute-specifier-seq decl-specifier-seq init-declarator-list ;
    attribute-specifier-seq? decl-specifier-seq ref-qualifier? [ identifier-list ] initializer ;

static_assert-declaration:
    static_assert ( constant-expression ) ;
    static_assert ( constant-expression , string-literal ) ;

empty-declaration:
    ;

attribute-declaration:
    attribute-specifier-seq ;

identifier-list:
    identifier
    identifier-list , identifier
"""

import glrp
from ...parser import cxx98, cxx11, cxx17, cxx20, cxx98_merge
from motor_typing import TYPE_CHECKING
from . import specifier
from . import declarator
from . import initializer
from . import function
from . import enumeration
from . import using_enum
from . import namespace
from . import using
from . import asm
from . import linkage
from . import attribute


@glrp.rule('declaration-seq? : declaration-seq declaration')
@glrp.rule('declaration-seq? : declaration')
@glrp.rule('declaration-seq? : ')
@cxx98
def declaration_seq_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declaration-seq : declaration')
@glrp.rule('declaration-seq : declaration-seq declaration')
@cxx98
def declaration_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declaration : block-declaration')
@glrp.rule('declaration : nodeclspec-function-declaration')
@glrp.rule('declaration : function-definition')
@glrp.rule('declaration : template-declaration')
@glrp.rule('declaration : explicit-instantiation')
@glrp.rule('declaration : explicit-specialization')
@glrp.rule('declaration : linkage-specification')
@glrp.rule('declaration : namespace-definition')
@glrp.rule('declaration : empty-declaration')
@cxx98
def declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declaration : attribute-declaration')
@cxx11
def declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declaration : deduction-guide')
@cxx17
def declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declaration : export-declaration')
@glrp.rule('declaration[prec:right,0] : module-import-declaration')
@cxx20
def declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('block-declaration : simple-declaration')
@glrp.rule('block-declaration : asm-declaration')
@glrp.rule('block-declaration : namespace-alias-definition')
@glrp.rule('block-declaration : using-declaration')
@glrp.rule('block-declaration : using-directive')
@glrp.rule('block-declaration : alias-declaration')
@cxx98
def block_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('block-declaration : static_assert-declaration')
@glrp.rule('block-declaration : opaque-enum-declaration')
@cxx11
def block_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('block-declaration : using-enum-declaration')
@cxx20
def block_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'nodeclspec-function-declaration : begin-nodeclspec-function-declaration attribute-specifier-seq? declarator ";"'
)
@cxx98
def nodeclspec_function_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


# todo: attribute-specifier-seq?, typename? not allowed
@glrp.rule(
    'alias-declaration : attribute-specifier-seq? "using" "typename"? "identifier" attribute-specifier-seq? "=" defining-type-id ";"'
)
@cxx98
def alias_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'simple-declaration : begin-simple-declaration attribute-specifier-seq? decl-specifier-seq init-declarator-list? ";"'
)
@glrp.rule(
    'simple-declaration : begin-simple-declaration attribute-specifier-seq? decl-specifier-seq begin-declarator-initializer ref-qualifier? "[" identifier-list "]" initializer ";"'
)
@cxx98
def simple_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('static_assert-declaration : "static_assert" "(" constant-expression "," "string-literal" ")" ";"')
@cxx11
def static_assert_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('static_assert-declaration : "static_assert" "(" constant-expression ")" ";"')
@cxx17
def static_assert_declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('empty-declaration : [prec:left,1]";"')
@cxx98
def empty_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('attribute-declaration : attribute-specifier-seq ";"')
@cxx11
def attribute_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('identifier-list : "identifier"')
@glrp.rule('identifier-list : identifier-list "," "identifier"')
@cxx98
def identifier_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('begin-nodeclspec-function-declaration : [split:nodeclspec_function_declaration]')
@glrp.rule('begin-simple-declaration : [split:simple_declaration]')
@glrp.rule('begin-decl-other : [split:decl_other]')
@glrp.rule('begin-decl-nodeclspec : [split:decl_nodeclspec]')
@cxx98
def begin_decl(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('begin-decl-deduction-guide : [split:decl_deduction_guide]')
@cxx17
def begin_decl_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('block-declaration')
@cxx98_merge
def ambiguous_block_declaration(self, decl_other, simple_declaration):
    # type: (CxxParser, Any, Any) -> Any
    pass


@glrp.merge('declaration')
@cxx98_merge
def ambiguous_declaration(
    self, decl_deduction_guide, ambiguous_block_declaration, ambiguous_function_definition,
    nodeclspec_function_declaration, decl_other
):
    # type: (CxxParser, Any, Any, Any, Any, Any) -> Any
    pass


@glrp.merge('simple-declaration')
@cxx98_merge
def ambiguous_simple_declaration(self, declarator_initializer, ambiguous_init_declarator):
    # type: (CxxParser, Any, Any) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser
