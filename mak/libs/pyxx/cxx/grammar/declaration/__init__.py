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
from ...parser import cxx98, cxx11, cxx17, cxx20
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


@glrp.rule('declaration : noexport-declaration')
@cxx98
def declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declaration : export-declaration')
@glrp.rule('declaration : module-import-declaration')
@cxx20
def declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('noexport-declaration-seq? : noexport-declaration-seq? noexport-declaration')
@glrp.rule('noexport-declaration-seq? :')
@cxx20
def noexport_declaration_seq_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('noexport-declaration : block-declaration')
@glrp.rule('noexport-declaration : nodeclspec-function-declaration')
@glrp.rule('noexport-declaration : function-definition')
@glrp.rule('noexport-declaration : template-declaration')
@glrp.rule('noexport-declaration : explicit-instantiation')
@glrp.rule('noexport-declaration : explicit-specialization')
@glrp.rule('noexport-declaration : linkage-specification')
@glrp.rule('noexport-declaration : namespace-definition')
@glrp.rule('noexport-declaration : empty-declaration')
@cxx98
def noexport_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('noexport-declaration : attribute-declaration')
@cxx11
def noexport_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('noexport-declaration : deduction-guide')
@cxx17
def noexport_declaration_cxx17(self, p):
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


@glrp.rule('nodeclspec-function-declaration : attribute-specifier-seq? declarator ";"')
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


@glrp.rule('simple-declaration : attribute-specifier-seq? decl-specifier-seq init-declarator-list? ";"')
@glrp.rule(
    'simple-declaration : attribute-specifier-seq? decl-specifier-seq ref-qualifier? "[" identifier-list "]" initializer ";"'
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


if TYPE_CHECKING:
    from ...parser import CxxParser