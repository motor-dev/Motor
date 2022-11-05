"""
type-id:
    type-specifier-seq abstract-declarator?

defining-type-id:
    defining-type-specifier-seq abstract-declarator?

abstract-declarator:
    ptr-abstract-declarator
    noptr-abstract-declarator? parameters-and-qualifiers trailing-return-type
    abstract-pack-declarator

ptr-abstract-declarator:
    noptr-abstract-declarator
    ptr-operator ptr-abstract-declarator?

noptr-abstract-declarator:
    noptr-abstract-declarator? parameters-and-qualifiers
    noptr-abstract-declarator? [ constant-expression? ] attribute-specifier-seq?
    ( ptr-abstract-declarator )

abstract-pack-declarator:
    noptr-abstract-pack-declarator
    ptr-operator abstract-pack-declarator

noptr-abstract-pack-declarator:
    noptr-abstract-pack-declarator parameters-and-qualifiers
    noptr-abstract-pack-declarator [ constant-expression? ] attribute-specifier-seq?
    ...
"""

import glrp
from ....parser import cxx98, cxx11, cxx98_merge
from .....ast.types import AmbiguousTypeId, TypeIdDeclarator, AmbiguousAbstractDeclarator, AbstractDeclaratorList, DeclaratorElementMethod, DeclaratorElementArray, DeclaratorElementAbstractPackId
from motor_typing import TYPE_CHECKING


@glrp.rule('type-id : type-specifier-seq [prec:nonassoc,0][split:end_declarator_list]')
@glrp.rule('defining-type-id : defining-type-specifier-seq ')
@cxx98
def type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeIdDeclarator(p[0], None)


@glrp.rule('type-id : [no-merge-warning]type-specifier-seq abstract-declarator')
@glrp.rule('defining-type-id : [no-merge-warning]defining-type-specifier-seq abstract-declarator')
@cxx98
def type_id_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeIdDeclarator(p[0], p[1])


@glrp.rule('abstract-declarator : ptr-abstract-declarator')
@cxx98
def abstract_declarator_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('abstract-declarator : parameters-and-qualifiers trailing-return-type')
@cxx11
def abstract_declarator_opt_method_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AbstractDeclaratorList([DeclaratorElementMethod(p[0][0], p[1], p[0][1], p[0][2], p[0][3], p[0][4])])


@glrp.rule('abstract-declarator : noptr-abstract-declarator parameters-and-qualifiers trailing-return-type')
@cxx11
def abstract_declarator_opt_noptr_method_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AbstractDeclaratorList(p[0] + [DeclaratorElementMethod(p[1][0], p[2], p[1][1], p[1][2], p[1][3], p[1][4])])


@glrp.rule('abstract-declarator : abstract-pack-declarator')
@cxx11
def abstract_declarator_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AbstractDeclaratorList([p[0]])


@glrp.rule('ptr-abstract-declarator : noptr-abstract-declarator [prec:nonassoc,0][split:end_declarator_list]')
@glrp.rule('ptr-abstract-declarator? : noptr-abstract-declarator [prec:nonassoc,0][split:end_declarator_list]')
@cxx98
def ptr_abstract_declarator_noptr(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('ptr-abstract-declarator : ptr-operator ptr-abstract-declarator?')
@glrp.rule('ptr-abstract-declarator? : ptr-operator ptr-abstract-declarator?')
@cxx98
def ptr_abstract_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    if p[1] is not None:
        return p[1] + [p[0]]
    else:
        return [p[0]]


@glrp.rule('ptr-abstract-declarator? : [prec:nonassoc,0][split:end_declarator_list]')
@cxx98
def ptr_abstract_declarator_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.rule('noptr-abstract-declarator : parameters-and-qualifiers')
@cxx98
def noptr_abstract_declarator_parameters_and_qualifiers(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [DeclaratorElementMethod(p[0][0], None, p[0][1], p[0][2], p[0][3], p[0][4])]


@glrp.rule('noptr-abstract-declarator : noptr-abstract-declarator parameters-and-qualifiers')
@cxx98
def noptr_abstract_declarator_noptr_parameters_and_qualifiers(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0] + [DeclaratorElementMethod(p[1][0], None, p[1][1], p[1][2], p[1][3], p[1][4])]


@glrp.rule(
    'noptr-abstract-declarator : noptr-abstract-declarator? "[" constant-expression? "]" attribute-specifier-seq?'
)
@cxx98
def noptr_abstract_declarator_array(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    if p[0] is not None:
        return p[0] + [DeclaratorElementArray(p[2], p[4])]
    else:
        return [DeclaratorElementArray(p[2], p[4])]


@glrp.rule(
    'noptr-abstract-declarator : [prec:nonassoc,0][split:continue_declarator_list] "(" begin-ptr-declarator ptr-abstract-declarator ")"'
)
@cxx98
def noptr_abstract_declarator_ptr(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[2]


@glrp.rule('noptr-abstract-declarator? : noptr-abstract-declarator')
@cxx98
def noptr_abstract_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('noptr-abstract-declarator? : ')
@cxx98
def noptr_abstract_declarator_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.rule('abstract-pack-declarator : noptr-abstract-pack-declarator [prec:nonassoc,0][split:end_declarator_list]')
@cxx11
def abstract_pack_declarator_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('abstract-pack-declarator : ptr-operator abstract-pack-declarator')
@cxx11
def abstract_pack_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1] + [p[0]]


@glrp.rule('noptr-abstract-pack-declarator : noptr-abstract-pack-declarator parameters-and-qualifiers')
@cxx11
def noptr_abstract_pack_declarator_parameters_and_qualifiers(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0] + [DeclaratorElementMethod(p[1][0], None, p[1][1], p[1][2], p[1][3], p[1][4])]


@glrp.rule(
    'noptr-abstract-pack-declarator : noptr-abstract-pack-declarator "[" constant-expression? "]" attribute-specifier-seq?'
)
@cxx11
def noptr_abstract_pack_declarator_array(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0] + [DeclaratorElementArray(p[2], p[4])]


@glrp.rule('noptr-abstract-pack-declarator : [prec:nonassoc,0][split:continue_declarator_list]"..."')
@cxx11
def noptr_abstract_pack_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [DeclaratorElementAbstractPackId()]


@glrp.merge('abstract-declarator')
@cxx98_merge
def ambiguous_abstract_declarator_2(self, ambiguous_noptr_abstract_declarator, parameter_declaration_clause):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    declarators = ambiguous_noptr_abstract_declarator + parameter_declaration_clause
    if len(declarators) == 1:
        return declarators[0]
    else:
        return AmbiguousAbstractDeclarator(declarators)


@glrp.merge('noptr-abstract-declarator')
@cxx98_merge
def ambiguous_noptr_abstract_declarator(self, ptr_declarator, parameter_declaration_clause):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    declarator_list = ptr_declarator + parameter_declaration_clause
    assert len(declarator_list) == 1
    return declarator_list[0]


@glrp.merge('type-id')
@cxx98_merge
def ambiguous_type_id(self, ambiguous_simple_type_specifier_2, ambiguous_template_argument_list_ellipsis):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('defining-type-id')
@cxx98_merge
def ambiguous_defining_type_id(self, ambiguous_simple_type_specifier_2, ambiguous_template_argument_list_ellipsis):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('type-id')
@cxx98_merge
def ambiguous_type_id_final(self, final_keyword, final_identifier):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return None    #TODO
    else:
        assert len(final_identifier) > 1
        return None    #TODO


@glrp.merge('defining-type-id')
@cxx98_merge
def ambiguous_defining_type_id_final(self, final_keyword, final_identifier):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return None    #TODO
    else:
        assert len(final_identifier) > 1
        return None    #TODO


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser