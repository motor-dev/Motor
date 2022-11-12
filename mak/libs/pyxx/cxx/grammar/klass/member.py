"""
member-specification:
    member-declaration member-specification?
    access-specifier : member-specification?

member-declaration:
    attribute-specifier-seq? decl-specifier-seq? member-declarator-list? ;
    function-definition
    using-declaration
    using-enum-declaration
    static_assert-declaration
    template-declaration
    explicit-specialization
    deduction-guide
    alias-declaration
    opaque-enum-declaration
    empty-declaration

member-declarator-list:
    member-declarator
    member-declarator-list , member-declarator

member-declarator:
    declarator virt-specifier-seq? pure-specifier?
    declarator requires-clause
    declarator brace-or-equal-initializer?
    identifier? attribute-specifier-seq? : constant-expression brace-or-equal-initializer?

virt-specifier-seq:
    virt-specifier
    virt-specifier-seq virt-specifier

virt-specifier:
    override
    final

pure-specifier:
    = 0
"""

import glrp
from ...parser import cxx98, cxx11, cxx17, cxx20, cxx98_merge
from ....ast.declarations import AmbiguousDeclaration
from motor_typing import TYPE_CHECKING


@glrp.rule('member-specification? : member-declaration member-specification?')
@glrp.rule('member-specification? : access-specifier ":" member-specification?')
@glrp.rule('member-specification? : ')
@cxx98
def member_specification_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


#@glrp.rule('member-declaration : attribute-specifier-seq? begin-declaration ";"')
@glrp.rule('member-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq? ";"')
@glrp.rule(
    'member-declaration : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? member-declarator-list ";"'
)
@glrp.rule('member-declaration : function-definition')
@glrp.rule('member-declaration : using-declaration')
@glrp.rule('member-declaration : template-declaration')
@glrp.rule('member-declaration : explicit-specialization')
@glrp.rule('member-declaration : alias-declaration')
@glrp.rule('member-declaration : empty-declaration')
@cxx98
def member_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('member-declaration : static_assert-declaration')
@glrp.rule('member-declaration : opaque-enum-declaration')
@cxx11
def member_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('member-declaration : deduction-guide')
@cxx17
def member_declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('member-declaration : using-enum-declaration')
@cxx20
def member_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('member-declarator-list : member-declarator')
@glrp.rule('member-declarator-list : member-declarator-list "," member-declarator')
@cxx98
def member_declarator_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('member-declarator : declarator')
@glrp.rule('member-declarator : declarator-function-body virt-specifier-seq')
@glrp.rule('member-declarator : declarator-function-body pure-specifier')
@glrp.rule('member-declarator : declarator-function-body virt-specifier-seq pure-specifier')
@glrp.rule('member-declarator : declarator-initializer brace-or-equal-initializer')
@glrp.rule('member-declarator : attribute-specifier-seq? ":" begin-bitfield constant-expression')
@glrp.rule(
    'member-declarator : attribute-specifier-seq? ":" begin-bitfield [no-merge-warning]constant-expression brace-or-equal-initializer'
)
@glrp.rule('member-declarator : declarator-initializer ":" begin-bitfield constant-expression')
@glrp.rule(
    'member-declarator : declarator-initializer ":" begin-bitfield constant-expression brace-or-equal-initializer'
)
@cxx98
def member_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('member-declarator : declarator-function-body requires-clause')
@cxx20
def member_declarator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('virt-specifier-seq : virt-specifier-seq virt-specifier')
@glrp.rule('virt-specifier-seq : virt-specifier')
@cxx98
def virt_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('virt-specifier : "virt-specifier-macro"')
@cxx98
def virt_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('virt-specifier : "virt-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def virt_specifier_function(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('virt-specifier : "override"')
@glrp.rule('virt-specifier : "final"')
@cxx11
def virt_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # TODO: accept macro_virt_specifier
    pass


@glrp.rule('pure-specifier : "=" "integer-literal"')
@cxx98
def pure_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-bitfield : [split:bitfield_declaration]')
@glrp.rule('begin-ctor-initializer : [split:constructor_declaration]')
@cxx98
def member_declarator_begin(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('member-declarator')
@cxx98_merge
def ambiguous_member_declarator(self, initializer, function_body):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('member-declarator')
@cxx98_merge
def ambiguous_member_declarator_2(self, ambiguous_constant_expression, ambiguous_initializer_clause):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('member-declaration')
@cxx98_merge
def ambiguous_member_declaration_deduction(self, ambiguous_simple_declaration, decl_deduction_guide):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('member-declaration')
@cxx98_merge
def ambiguous_member_declaration(
    self, decl_specifier_seq_end, decl_specifier_seq_continue, ambiguous_function_definition
):
    # type: (CxxParser, List[Any], List[Any], List[Any]) -> Any
    pass


@glrp.merge('member-declaration')
@cxx98_merge
def ambiguous_member_declaration_2(self, bitfield_declaration, constructor_declaration):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('member-declaration')
@cxx98_merge
def ambiguous_member_declaration_3(self, initializer, function_body):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    # This method is actually not called because the initializer and the function_body
    # options will raise syntax errors for invalid combinations
    #assert False
    pass


@glrp.merge('member-declaration')
@cxx98_merge
def ambiguous_member_declaration_final(self, final_keyword, final_identifier):
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
    from ...parser import CxxParser