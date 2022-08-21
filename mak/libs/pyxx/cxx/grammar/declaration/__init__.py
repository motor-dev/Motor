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
from ...parser import cxx98, cxx11, cxx17, cxx20, cxx98_merge, cxx20_merge
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


@glrp.rule('declaration-proxy : block-declaration')
@glrp.rule('declaration-proxy : nodeclspec-function-declaration')
@glrp.rule('declaration-proxy : function-definition')
@glrp.rule('declaration-proxy : template-declaration')
@glrp.rule('declaration-proxy : explicit-instantiation')
@glrp.rule('declaration-proxy : explicit-specialization')
@glrp.rule('declaration-proxy : linkage-specification')
@glrp.rule('declaration-proxy : namespace-definition')
@glrp.rule('declaration-proxy : empty-declaration')
@cxx98
def declaration_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declaration-proxy : attribute-declaration')
@cxx11
def declaration_proxy_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declaration-proxy : deduction-guide')
@cxx17
def declaration_proxy_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declaration-proxy : export-declaration')
@glrp.rule('declaration-proxy[prec:right,0] : module-import-declaration')
@cxx20
def declaration_proxy_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('declaration-proxy')
@cxx20_merge
def ambiguous_explicit_declaration(self, explicit_deduction, explicit_declaration):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('declaration-proxy')
@cxx98_merge
def ambiguous_declaration(
    self, nodeclspec_function_declaration, ambiguous_function_definition, template_decl, deduction_guide,
    ambiguous_block_declaration
):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('declaration-proxy')
@cxx98_merge
def ambiguous_declaration_init_list(self, braced_init_list, compound_statement):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.rule('declaration : declaration-proxy')
@cxx98
def declaration(self, p):
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


@glrp.merge('block-declaration')
@cxx98_merge
def ambiguous_block_declaration(self, simple_declaration, opaque_enum_declaration):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
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


@glrp.merge('simple-declaration')
@glrp.merge_result('simple_declaration')
@cxx98_merge
def simple_declaration_rename(self, ambiguous_decl_specifier_seq):
    # type: (CxxParser, Optional[glrp.Production]) -> None
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


@glrp.merge('nodeclspec-function-declaration')
@glrp.merge_result('nodeclspec_function_declaration')
@cxx98_merge
def nodeclspec_function_declaration_rename(self, ambiguous_declarator):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from motor_typing import Optional
    from ...parser import CxxParser
