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
from ...parse import cxx98, cxx11, cxx17, cxx20, cxx98_merge
from ....ast.declarations import AmbiguousDeclaration, SimpleDeclaration, StructuredBindingDeclaration, StaticAssert, AliasDeclaration
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


@glrp.rule('declaration-seq? : ')
@cxx98
def declaration_seq_empty(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return []


@glrp.rule('declaration-seq : declaration')
@glrp.rule('declaration-seq? : declaration')
@cxx98
def declaration_seq_last(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [p[0]]


@glrp.rule('declaration-seq? : declaration-seq declaration')
@glrp.rule('declaration-seq : declaration-seq declaration')
@cxx98
def declaration_seq_recursive(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append(p[1])
    return result


@glrp.rule('declaration : block-declaration')
#@glrp.rule('declaration : nodeclspec-function-declaration')
@glrp.rule('declaration : function-definition')
@glrp.rule('declaration : template-declaration')
@glrp.rule('declaration : explicit-instantiation')
@glrp.rule('declaration : explicit-specialization')
@glrp.rule('declaration : linkage-specification')
@glrp.rule('declaration : namespace-definition')
@glrp.rule('declaration : empty-declaration')
@cxx98
def declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('declaration : attribute-declaration')
@cxx11
def declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('declaration : deduction-guide')
@cxx17
def declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('declaration : export-declaration')
@glrp.rule('declaration[prec:right,0] : module-import-declaration')
@cxx20
def declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('block-declaration : simple-declaration')
@glrp.rule('block-declaration : asm-declaration')
@glrp.rule('block-declaration : namespace-alias-definition')
@glrp.rule('block-declaration : using-declaration')
@glrp.rule('block-declaration : using-directive')
@glrp.rule('block-declaration : alias-declaration')
@cxx98
def block_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('block-declaration : static_assert-declaration')
@glrp.rule('block-declaration : opaque-enum-declaration')
@cxx11
def block_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('block-declaration : using-enum-declaration')
@cxx20
def block_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


#@glrp.rule(
#    'nodeclspec-function-declaration : attribute-specifier-seq? begin-declaration declarator ";"'
#)
#@cxx98
#def nodeclspec_function_declaration(self, p):
#    # type: (CxxParser, glrp.Production) -> Any
#    return SimpleDeclaration(p[0], None, [InitDeclarator(p[3], p[2], None)])


# todo: attribute-specifier-seq?, typename? not allowed
@glrp.rule(
    'alias-declaration : attribute-specifier-seq? begin-declaration "using" "typename"? "identifier" attribute-specifier-seq? "=" defining-type-id ";"'
)
@cxx98
def alias_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AliasDeclaration(p[0], p[4], p[5], p[7])


@glrp.rule('simple-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq? ";"')
@cxx98
def simple_declaration_no_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleDeclaration(p[0], p[2], None)


@glrp.rule(
    'simple-declaration : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? init-declarator-list ";"'
)
@cxx98
def simple_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleDeclaration(p[0], p[2], p[3])


@glrp.rule(
    'simple-declaration :  attribute-specifier-seq? begin-declaration decl-specifier-seq? ref-qualifier? "[" identifier-list "]" initializer ";"'
)
@cxx17
def simple_declaration_structured_binding_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StructuredBindingDeclaration(p[0], p[2], p[3], p[5], p[6])


@glrp.rule('static_assert-declaration : "static_assert" "(" constant-expression "," string-literal-list ")" ";"')
@cxx11
def static_assert_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StaticAssert(p[2], p[4])


@glrp.rule('static_assert-declaration : "static_assert" "(" constant-expression ")" ";"')
@cxx17
def static_assert_declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StaticAssert(p[2], None)


@glrp.rule('empty-declaration : [prec:left,1]";"')
@cxx98
def empty_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleDeclaration([], None, None)


@glrp.rule('attribute-declaration : attribute-specifier-seq? [prec:right,1]";"')
@cxx11
def attribute_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleDeclaration(p[0], None, None)


@glrp.rule('identifier-list : "identifier"')
@cxx17
def identifier_list_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [p[0].value]


@glrp.rule('identifier-list : identifier-list "," "identifier"')
@cxx17
def identifier_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append(p[2].value)
    return result


@glrp.rule('begin-declaration : [split:simple_declaration]')
@cxx98
def begin_decl(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-decl-deduction-guide : [split:decl_deduction_guide]')
@cxx17
def begin_decl_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('declaration')
@cxx98_merge
def ambiguous_declaration(self, continue_declarator_list, ambiguous_init_declarator_initializer):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousDeclaration(continue_declarator_list + ambiguous_init_declarator_initializer)


@glrp.merge('declaration')
@cxx98_merge
def ambiguous_declaration_deduction(
    self, ambiguous_simple_declaration, ambiguous_function_definition, decl_deduction_guide
):
    # type: (CxxParser, List[Any], List[Any], List[Any]) -> Any
    return AmbiguousDeclaration(ambiguous_simple_declaration + ambiguous_function_definition + decl_deduction_guide)


@glrp.merge('declaration')
@cxx98_merge
def ambiguous_declaration_2(self, initializer, function_body):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    # Only one set of options should be valid here
    if initializer:
        assert len(function_body) == 0
        return AmbiguousDeclaration(initializer)
    else:
        return AmbiguousDeclaration(function_body)


@glrp.merge('simple-declaration')
@cxx98_merge
def ambiguous_simple_declaration(self, simple_declaration, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any], List[Any]) -> Any
    return AmbiguousDeclaration(simple_declaration + decl_specifier_seq_end + decl_specifier_seq_continue)


@glrp.merge('simple-declaration')
@cxx98_merge
def ambiguous_simple_declaration_final(self, final_keyword, final_identifier):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return AmbiguousDeclaration(final_keyword)
    else:
        assert len(final_identifier) > 1
        return AmbiguousDeclaration(final_identifier)


if TYPE_CHECKING:
    from typing import Any, List
    from ...parse import CxxParser
