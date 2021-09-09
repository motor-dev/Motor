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
from ...parser import cxx98, cxx11, cxx17, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('member-specification? : member-declaration member-specification?')
@glrp.rule('member-specification? : access-specifier ":" member-specification?')
@glrp.rule('member-specification? : ')
@cxx98
def member_specification_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('member-declaration : attribute-specifier-seq? member-declarator-list? ";"')
@glrp.rule('member-declaration : attribute-specifier-seq? decl-specifier-seq member-declarator-list? ";"')
@glrp.rule('member-declaration : function-definition')
@glrp.rule('member-declaration : using-declaration')
@glrp.rule('member-declaration : template-declaration')
@glrp.rule('member-declaration : explicit-specialization')
@glrp.rule('member-declaration : alias-declaration')
@glrp.rule('member-declaration : empty-declaration')
@cxx98
def member_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('member-declaration : static_assert-declaration')
@glrp.rule('member-declaration : opaque-enum-declaration')
@cxx11
def member_declaration_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('member-declaration : deduction-guide')
@cxx17
def member_declaration_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('member-declaration : using-enum-declaration')
@cxx20
def member_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('member-declarator-list : member-declarator')
@glrp.rule('member-declarator-list : member-declarator-list "," member-declarator')
@cxx98
def member_declarator_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('member-declarator-list? : member-declarator')
@glrp.rule('member-declarator-list? : member-declarator-list "," member-declarator')
@glrp.rule('member-declarator-list? : ')
@cxx98
def member_declarator_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('member-declarator : declarator virt-specifier-seq? pure-specifier')
# TODO virt-specifier-seq? not allowed
@glrp.rule('member-declarator : declarator virt-specifier-seq? brace-or-equal-initializer')
@glrp.rule('member-declarator : attribute-specifier-seq? ":" constant-expression brace-or-equal-initializer?')
@glrp.rule(
    'member-declarator : identifier attribute-specifier-seq? ":" constant-expression brace-or-equal-initializer?'
)
@cxx98
def member_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('member-declarator : declarator requires-clause')
@cxx20
def member_declarator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('virt-specifier-seq? : virt-specifier-seq? virt-specifier')
@glrp.rule('virt-specifier-seq? : ')
@cxx98
def virt_specifier_seq_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('virt-specifier : "virt-specifier-macro"')
@cxx98
def virt_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('virt-specifier : "override"')
@glrp.rule('virt-specifier : "final"')
@cxx11
def virt_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: accept macro_virt_specifier
    pass


@glrp.rule('pure-specifier[split] : "=" "integer-literal"')
@cxx98
def pure_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser