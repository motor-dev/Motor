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
from ...parse import cxx98, cxx11, cxx17, cxx20, cxx98_merge
from ....ast.declarations import AmbiguousDeclaration, SimpleDeclaration, MemberInitDeclarator, InitDeclaratorList, AmbiguousInitDeclaratorList
from ....ast.function import VirtSpecifierMacro, VirtSpecifierFinal, VirtSpecifierOverride, VirtSpecifierPure
from ....ast.klass import AccessSpecifierDefault
from motor_typing import TYPE_CHECKING


@glrp.rule('member-specification? : member-declaration member-specification?')
@cxx98
def member_specification(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[1]
    result[0][1].insert(0, p[0])
    return result


@glrp.rule('member-specification? : access-specifier ":" member-specification?')
@cxx98
def member_specification_access_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [(AccessSpecifierDefault(), []), (p[0], p[2][0][1])] + p[2][1:]


@glrp.rule('member-specification? : ')
@cxx98
def member_specification_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [(AccessSpecifierDefault(), [])]


#@glrp.rule('member-declaration : attribute-specifier-seq? begin-declaration ";"')
@glrp.rule('member-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq? ";"')
@cxx98
def member_declaration_no_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleDeclaration(p[0], p[2], None)


@glrp.rule(
    'member-declaration : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? member-declarator-list ";"'
)
@cxx98
def member_declaration_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleDeclaration(p[0], p[2], p[3])


@glrp.rule('member-declaration : function-definition')
@glrp.rule('member-declaration : using-declaration')
@glrp.rule('member-declaration : template-declaration')
@glrp.rule('member-declaration : explicit-specialization')
@glrp.rule('member-declaration : alias-declaration')
@glrp.rule('member-declaration : empty-declaration')
@cxx98
def member_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('member-declaration : static_assert-declaration')
@glrp.rule('member-declaration : opaque-enum-declaration')
@cxx11
def member_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('member-declaration : deduction-guide')
@cxx17
def member_declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('member-declaration : using-enum-declaration')
@cxx20
def member_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('member-declarator-list : member-declarator')
@cxx98
def member_declarator_list_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return InitDeclaratorList(p[0], None)


@glrp.rule('member-declarator-list : member-declarator-list "," member-declarator')
@cxx98
def member_declarator_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0].add(p[2])


@glrp.rule('member-declarator : declarator')
@cxx98
def member_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(p[0], None, None, [], None)


@glrp.rule('member-declarator : declarator-function-body virt-specifier-seq')
@cxx98
def member_declarator_virt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(p[0], None, None, p[1], None)


@glrp.rule('member-declarator : declarator-function-body pure-specifier')
@cxx98
def member_declarator_pure(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(p[0], None, None, [p[1]], None)


@glrp.rule('member-declarator : declarator-function-body virt-specifier-seq pure-specifier')
@cxx98
def member_declarator_virt_pure(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(p[0], None, None, p[1] + [p[2]], None)


@glrp.rule('member-declarator : declarator-initializer brace-or-equal-initializer')
@cxx98
def member_declarator_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(p[0], p[1], None, [], None)


@glrp.rule('member-declarator : ":" constant-expression')
@cxx98
def member_declarator_bitfield_no_name(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(None, None, None, [], p[1])


@glrp.rule('member-declarator : ":" [no-merge-warning]constant-expression brace-or-equal-initializer')
@cxx98
def member_declarator_bitfield_no_name_inititalizer(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(None, p[2], None, [], p[1])


@glrp.rule('member-declarator : declarator-initializer ":" constant-expression')
@cxx98
def member_declarator_bitfield(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(p[0], None, None, [], p[2])


@glrp.rule('member-declarator : declarator-initializer ":" constant-expression brace-or-equal-initializer')
@cxx98
def member_declarator_bitfield_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(p[0], p[3], None, [], p[2])


@glrp.rule('member-declarator : declarator-function-body requires-clause')
@cxx20
def member_declarator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberInitDeclarator(p[0], None, p[1], [], None)


@glrp.rule('virt-specifier-seq : virt-specifier')
@cxx98
def virt_specifier_seq_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [p[0]]


@glrp.rule('virt-specifier-seq : virt-specifier-seq virt-specifier')
@cxx98
def virt_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append(p[1])
    return result


@glrp.rule('virt-specifier : "virt-specifier-macro"')
@cxx98
def virt_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return VirtSpecifierMacro(p[0], None)


@glrp.rule('virt-specifier : "virt-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def virt_specifier_function(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return VirtSpecifierMacro(p[0], p[2])


@glrp.rule('virt-specifier : "override"')
@cxx11
def virt_specifier_override_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return VirtSpecifierOverride()


@glrp.rule('virt-specifier : "final"')
@cxx11
def virt_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return VirtSpecifierFinal()


@glrp.rule('pure-specifier : "=" "integer-literal"')
@cxx98
def pure_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return VirtSpecifierPure()


@glrp.merge('member-declarator-list')
@cxx98_merge
def ambiguous_member_declarator_list(
    self, ambiguous_template_argument_list_ellipsis, id_template, ambiguous_initializer_clause,
    ambiguous_member_declarator_list
):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any]) -> Any
    return AmbiguousInitDeclaratorList(
        ambiguous_template_argument_list_ellipsis + id_template + ambiguous_initializer_clause +
        ambiguous_member_declarator_list
    )


@glrp.merge('member-declaration')
@cxx98_merge
def ambiguous_member_declaration_deduction(self, ambiguous_simple_declaration, decl_deduction_guide):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousDeclaration(ambiguous_simple_declaration + decl_deduction_guide)


@glrp.merge('member-declaration')
@cxx98_merge
def ambiguous_member_declaration(
    self, decl_specifier_seq_end, decl_specifier_seq_continue, ambiguous_function_definition
):
    # type: (CxxParser, List[Any], List[Any], List[Any]) -> Any
    return AmbiguousDeclaration(decl_specifier_seq_end + decl_specifier_seq_continue + ambiguous_function_definition)


@glrp.merge('member-declaration')
@cxx98_merge
def ambiguous_member_declaration_3(self, initializer, function_body):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    # This method is actually not called because the initializer and the function_body
    # Only one set of options should be valid here
    if initializer:
        assert len(function_body) == 0
        return AmbiguousDeclaration(initializer)
    else:
        return AmbiguousDeclaration(function_body)


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
    from ...parse import CxxParser