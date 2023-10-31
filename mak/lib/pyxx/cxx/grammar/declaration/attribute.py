"""
attribute-specifier-seq:
    attribute-specifier-seq? attribute-specifier

attribute-specifier:
    [ [ attribute-using-prefix? attribute-list ] ]
    alignment-specifier

alignment-specifier:
    alignas ( type-id ...? )
    alignas ( constant-expression ...? )

attribute-using-prefix:
    using attribute-namespace :

attribute-list:
    attribute?
    attribute-list , attribute?
    attribute ...
    attribute-list , attribute ...

attribute:
    attribute-token attribute-argument-clause?

attribute-token:
    identifier
    attribute-scoped-token

attribute-scoped-token:
    attribute-namespace :: identifier

attribute-namespace:
    identifier

attribute-argument-clause:
    ( balanced-token-seq? )

balanced-token-seq:
    balanced-token
    balanced-token-seq balanced-token

balanced-token:
    ( balanced-token-seq? )
    [ balanced-token-seq? ]
    { balanced-token-seq? }
    any token other than a parenthesis, a bracket, or a brace
"""

import glrp
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx11, cxx17, cxx20, cxx23, cxx11_merge
from ....ast.attributes import (
    AttributeDocumentation,
    InvalidAttribute,
    AttributeNamed,
    AttributeAlignAsExpression,
    AttributeAlignAsType,
    AttributeAlignAsAmbiguous,
    AttributeMacro,
    AttributeNamedList,
)
from ....ast.pack import PackExpandType, PackExpandExpression, PackExpandAttributeNamed


@glrp.rule('attribute-specifier-seq? : attribute-specifier-seq? attribute-specifier')
@cxx98
def attribute_specifier_seq(_: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(p[1])
    return result


@glrp.rule('attribute-specifier-seq? : [prec:right,0]')
@cxx98
def attribute_specifier_seq_opt(_: CxxParser, __: glrp.Production) -> Any:
    return []


# @glrp.rule('attribute-specifier : [prec:left,1]"doxycomment-line-start" "doxycomment-line-end"')
@glrp.rule('attribute-specifier : [prec:left,1]"doxycomment-block-start" "doxycomment-block-end"')
@cxx98
def attribute_specifier_documentation(_: CxxParser, p: glrp.Production) -> Any:
    return AttributeDocumentation(p[0])


@glrp.rule('attribute-specifier : [prec:left,1]"attribute-specifier-macro"')
@cxx98
def attribute_specifier_macro(_: CxxParser, p: glrp.Production) -> Any:
    return AttributeMacro(p[0].position, p[0].text(), None)


@glrp.rule('attribute-specifier : [prec:left,1]"attribute-specifier-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def attribute_specifier_macro_function(_: CxxParser, p: glrp.Production) -> Any:
    return AttributeMacro(p[0].position, p[0].text(), p[2])


@glrp.rule('attribute-specifier : [prec:left,1]"[[" attribute-using-prefix? attribute-list "]" "]"')
@cxx11
def attribute_specifier_named_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return AttributeNamedList(p[1], p[2])


@glrp.rule('attribute-specifier : [prec:left,1]"[[" "#error" "]" "]"')
@cxx11
def attribute_error_cxx11(_: CxxParser, __: glrp.Production) -> Any:
    return InvalidAttribute()


@glrp.rule('attribute-specifier : alignment-specifier')
@cxx11
def attribute_specifier_alignment_specifier_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('alignment-specifier : [prec:left,1]"alignas" "(" begin-type-id [no-merge-warning] type-id "..."? ")"')
@cxx11
def alignment_specifier_alignment_specifier_type_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    if p[4]:
        return AttributeAlignAsType(PackExpandType(p[3]))
    else:
        return AttributeAlignAsType(p[3])


@glrp.rule('alignment-specifier : [prec:left,1]"alignas" "(" begin-expression constant-expression "..."? ")"')
@cxx11
def alignment_specifier_alignment_specifier_expression_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    if p[4]:
        return AttributeAlignAsExpression(PackExpandExpression(p[3]))
    else:
        return AttributeAlignAsExpression(p[3])


@glrp.rule('alignment-specifier : [prec:left,1]"alignas" "(" "#error" ")"')
@cxx11
def alignment_specifier_alignment_specifier_error_cxx11(_: CxxParser, __: glrp.Production) -> Any:
    return InvalidAttribute()


@glrp.rule('attribute-using-prefix? : "using" attribute-namespace ":"')
@cxx17
def attribute_using_prefix_opt_cxx17(_: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('attribute-using-prefix? : ')
@cxx11
def attribute_using_prefix_opt_empty_cxx11(_: CxxParser, __: glrp.Production) -> Any:
    return None


@glrp.rule('attribute-list : attribute?')
@cxx11
def attribute_list_end_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    if p[0] is not None:
        return [p[0]]
    else:
        return []


@glrp.rule('attribute-list : attribute-list "," attribute?')
def attribute_list_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    if p[2] is not None:
        result.append(p[2])
    return result


@glrp.rule('attribute-list : attribute "..."')
@cxx11
def attribute_list_end_pack_expand_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return [PackExpandAttributeNamed(p[0])]


@glrp.rule('attribute-list : attribute-list "," attribute "..."')
@cxx11
def attribute_list_pack_expand_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(PackExpandAttributeNamed(p[2]))
    return result


@glrp.rule('attribute? : attribute-token attribute-argument-clause?')
@glrp.rule('attribute : attribute-token attribute-argument-clause?')
@cxx11
def attribute_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return AttributeNamed(p[0][0], p[0][1], p[1], p[0][2])


@glrp.rule('attribute? : ')
@cxx11
def attribute_opt_empty_cxx11(_: CxxParser, __: glrp.Production) -> Any:
    return None


@glrp.rule('attribute-token : "identifier"')
@cxx11
def attribute_token_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return None, p[0].value, p[0].position


@glrp.rule('attribute-token : attribute-scoped-token')
@cxx11
def attribute_token_scoped_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('attribute-scoped-token : attribute-namespace "::" "identifier"')
@cxx11
def attribute_scoped_token_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return p[0], p[2].value, p[2].position


@glrp.rule('attribute-namespace : "identifier"')
@cxx11
def attribute_namespace_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return p[0].value


@glrp.rule('attribute-argument-clause? : "(" balanced-token-seq? ")"')
@cxx11
def attribute_argument_clause_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('attribute-argument-clause? : ')
@cxx11
def attribute_argument_clause_opt_cxx11(_: CxxParser, __: glrp.Production) -> Any:
    return None


@glrp.rule('balanced-token-seq? : balanced-token-seq? balanced-token')
@cxx98
def balanced_token_seq(_: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(p[1])
    return result


@glrp.rule('balanced-token-seq? : balanced-token-seq? "(" balanced-token-seq? ")"')
@glrp.rule('balanced-token-seq? : balanced-token-seq? "[" balanced-token-seq? "]"')
@glrp.rule('balanced-token-seq? : balanced-token-seq? "{" balanced-token-seq? "}"')
@cxx98
def balanced_token_seq_bracket(_: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(p[1])
    result += p[2]
    result.append(p[3])
    return result


@glrp.rule('balanced-token-seq? :')
@cxx98
def balanced_token_seq_opt(_: CxxParser, __: glrp.Production) -> Any:
    return []


@glrp.rule('balanced-token : "asm"')
@glrp.rule('balanced-token : "auto"')
@glrp.rule('balanced-token : "bool"')
@glrp.rule('balanced-token : "break"')
@glrp.rule('balanced-token : "case"')
@glrp.rule('balanced-token : "catch"')
@glrp.rule('balanced-token : "char"')
@glrp.rule('balanced-token : "class"')
@glrp.rule('balanced-token : "const"')
@glrp.rule('balanced-token : "const_cast"')
@glrp.rule('balanced-token : "continue"')
@glrp.rule('balanced-token : "default"')
@glrp.rule('balanced-token : "delete"')
@glrp.rule('balanced-token : "do"')
@glrp.rule('balanced-token : "double"')
@glrp.rule('balanced-token : "dynamic_cast"')
@glrp.rule('balanced-token : "else"')
@glrp.rule('balanced-token : "enum"')
@glrp.rule('balanced-token : "explicit"')
@glrp.rule('balanced-token : "extern"')
@glrp.rule('balanced-token : "false"')
@glrp.rule('balanced-token : "float"')
@glrp.rule('balanced-token : "for"')
@glrp.rule('balanced-token : "friend"')
@glrp.rule('balanced-token : "goto"')
@glrp.rule('balanced-token : "if"')
@glrp.rule('balanced-token : "inline"')
@glrp.rule('balanced-token : "int"')
@glrp.rule('balanced-token : "long"')
@glrp.rule('balanced-token : "mutable"')
@glrp.rule('balanced-token : "namespace"')
@glrp.rule('balanced-token : "new"')
@glrp.rule('balanced-token : "operator"')
@glrp.rule('balanced-token : "private"')
@glrp.rule('balanced-token : "protected"')
@glrp.rule('balanced-token : "public"')
@glrp.rule('balanced-token : "register"')
@glrp.rule('balanced-token : "reinterpret_cast"')
@glrp.rule('balanced-token : "return"')
@glrp.rule('balanced-token : "short"')
@glrp.rule('balanced-token : "signed"')
@glrp.rule('balanced-token : "sizeof"')
@glrp.rule('balanced-token : "static"')
@glrp.rule('balanced-token : "static_cast"')
@glrp.rule('balanced-token : "struct"')
@glrp.rule('balanced-token : "switch"')
@glrp.rule('balanced-token : "template"')
@glrp.rule('balanced-token : "this"')
@glrp.rule('balanced-token : "throw"')
@glrp.rule('balanced-token : "true"')
@glrp.rule('balanced-token : "try"')
@glrp.rule('balanced-token : "typedef"')
@glrp.rule('balanced-token : "typeid"')
@glrp.rule('balanced-token : "typename"')
@glrp.rule('balanced-token : "union"')
@glrp.rule('balanced-token : "unsigned"')
@glrp.rule('balanced-token : "using"')
@glrp.rule('balanced-token : "virtual"')
@glrp.rule('balanced-token : "void"')
@glrp.rule('balanced-token : "volatile"')
@glrp.rule('balanced-token : "wchar_t"')
@glrp.rule('balanced-token : "while"')
@glrp.rule('balanced-token : "+"')
@glrp.rule('balanced-token : "-"')
@glrp.rule('balanced-token : "*"')
@glrp.rule('balanced-token : "/"')
@glrp.rule('balanced-token : "%"')
@glrp.rule('balanced-token : "|"')
@glrp.rule('balanced-token : "&"')
@glrp.rule('balanced-token : "~"')
@glrp.rule('balanced-token : "^"')
@glrp.rule('balanced-token : "<<"')
# @glrp.rule('balanced-token : ">>"')
@glrp.rule('balanced-token : "%>"')
@glrp.rule('balanced-token : "||"')
@glrp.rule('balanced-token : "&&"')
@glrp.rule('balanced-token : "!"')
@glrp.rule('balanced-token : "<"')
@glrp.rule('balanced-token : ">"')
@glrp.rule('balanced-token : "<="')
@glrp.rule('balanced-token : ">="')
@glrp.rule('balanced-token : "=="')
@glrp.rule('balanced-token : "!="')
@glrp.rule('balanced-token : "="')
@glrp.rule('balanced-token : "*="')
@glrp.rule('balanced-token : "/="')
@glrp.rule('balanced-token : "%="')
@glrp.rule('balanced-token : "+="')
@glrp.rule('balanced-token : "-="')
@glrp.rule('balanced-token : "<<="')
@glrp.rule('balanced-token : ">>="')
@glrp.rule('balanced-token : "&="')
@glrp.rule('balanced-token : "|="')
@glrp.rule('balanced-token : "^="')
@glrp.rule('balanced-token : "++"')
@glrp.rule('balanced-token : "--"')
@glrp.rule('balanced-token : "->"')
@glrp.rule('balanced-token : "->*"')
@glrp.rule('balanced-token : ".*"')
@glrp.rule('balanced-token : "?"')
@glrp.rule('balanced-token : "::"')
@glrp.rule('balanced-token : ","')
@glrp.rule('balanced-token : "."')
@glrp.rule('balanced-token : ";"')
@glrp.rule('balanced-token : ":"')
@glrp.rule('balanced-token : "..."')
@glrp.rule('balanced-token : "%identifier"')
@glrp.rule('balanced-token : "floating-literal"')
@glrp.rule('balanced-token : "integer-literal"')
@glrp.rule('balanced-token : "string-literal"')
@glrp.rule('balanced-token : "character-literal"')
@glrp.rule('balanced-token : "virt-specifier-macro"')
@glrp.rule('balanced-token : "virt-specifier-macro-function"')
@glrp.rule('balanced-token : "access-specifier-macro"')
@glrp.rule('balanced-token : "access-specifier-macro-function"')
@glrp.rule('balanced-token : "decl-specifier-macro"')
@glrp.rule('balanced-token : "decl-specifier-macro-function"')
@glrp.rule('balanced-token : "attribute-specifier-macro"')
@glrp.rule('balanced-token : "attribute-specifier-macro-function"')
@glrp.rule('balanced-token : "storage-class-specifier-macro"')
@glrp.rule('balanced-token : "storage-class-specifier-macro-function"')
@glrp.rule('balanced-token : "decltype-macro"')
@glrp.rule('balanced-token : "type-trait-macro"')
@glrp.rule('balanced-token : "type-trait-macro-function"')
@cxx98
def balanced_token(_: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('balanced-token : "alignas"')
@glrp.rule('balanced-token : "alignof"')
@glrp.rule('balanced-token : "char16_t"')
@glrp.rule('balanced-token : "char32_t"')
@glrp.rule('balanced-token : "constexpr"')
@glrp.rule('balanced-token : "decltype"')
@glrp.rule('balanced-token : "final"')
@glrp.rule('balanced-token : "noexcept"')
@glrp.rule('balanced-token : "nullptr"')
@glrp.rule('balanced-token : "override"')
@glrp.rule('balanced-token : "static_assert"')
@glrp.rule('balanced-token : "thread_local"')
@glrp.rule('balanced-token : "user-defined-floating-literal"')
@glrp.rule('balanced-token : "user-defined-integer-literal"')
@glrp.rule('balanced-token : "user-defined-string-literal"')
@glrp.rule('balanced-token : "user-defined-character-literal"')
@cxx11
def balanced_token_cxx11(_: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('balanced-token : "char8_t"')
@glrp.rule('balanced-token : "concept"')
@glrp.rule('balanced-token : "consteval"')
@glrp.rule('balanced-token : "constinit"')
@glrp.rule('balanced-token : "co_await"')
@glrp.rule('balanced-token : "co_return"')
@glrp.rule('balanced-token : "co_yield"')
@glrp.rule('balanced-token : "export"')
@glrp.rule('balanced-token : "import"')
@glrp.rule('balanced-token : "module"')
@glrp.rule('balanced-token : "requires"')
@glrp.rule('balanced-token : "<=>"')
@cxx20
def balanced_token_cxx20(_: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('balanced-token : "atomic_cancel"')
@glrp.rule('balanced-token : "atomic_commit"')
@glrp.rule('balanced-token : "atomic_noexcept"')
@glrp.rule('balanced-token : "synchronized"')
@glrp.rule('balanced-token : "reflexpr"')
@cxx23
def balanced_token_cxx23(_: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.merge('alignment-specifier')
@cxx11_merge
def ambiguous_alignment_specifier(_: CxxParser, type_id: List[Any], expression: List[Any]) -> Any:
    assert len(expression) == 1
    assert len(type_id) == 1
    return AttributeAlignAsAmbiguous(type_id[0], expression[0])


@glrp.merge('alignment-specifier')
@cxx11_merge
def ambiguous_alignment_specifier_ellipsis(
        _: CxxParser, end_declarator_list: List[Any], __: List[Any]
) -> Any:
    # "..."
    assert len(end_declarator_list) == 1
    return end_declarator_list[0]
