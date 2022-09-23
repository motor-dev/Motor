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
from motor_typing import TYPE_CHECKING


@glrp.rule('type-id : [no-merge-warning] type-specifier-seq [split:end_declarator_list]')
@glrp.rule('type-id : [no-merge-warning] type-specifier-seq abstract-declarator')
@cxx98
def type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('defining-type-id : [no-merge-warning] defining-type-specifier-seq [split:end_declarator_list]')
@glrp.rule('defining-type-id : [no-merge-warning] defining-type-specifier-seq abstract-declarator')
@cxx98
def defining_type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('abstract-declarator : ptr-abstract-declarator')
@cxx98
def abstract_declarator_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('abstract-declarator : parameters-and-qualifiers trailing-return-type')
@glrp.rule('abstract-declarator : noptr-abstract-declarator parameters-and-qualifiers trailing-return-type')
@glrp.rule('abstract-declarator : abstract-pack-declarator')
@cxx11
def abstract_declarator_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('ptr-abstract-declarator : noptr-abstract-declarator [split:end_declarator_list]')
@glrp.rule('ptr-abstract-declarator : ptr-operator ptr-abstract-declarator?')
@cxx98
def ptr_abstract_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('ptr-abstract-declarator? : noptr-abstract-declarator [split:end_declarator_list]')
@glrp.rule('ptr-abstract-declarator? : ptr-operator ptr-abstract-declarator?')
@glrp.rule('ptr-abstract-declarator? : [split:end_declarator_list]')
@cxx98
def ptr_abstract_declarator_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('noptr-abstract-declarator : parameters-and-qualifiers')
@glrp.rule('noptr-abstract-declarator : noptr-abstract-declarator parameters-and-qualifiers')
@glrp.rule(
    'noptr-abstract-declarator : noptr-abstract-declarator? "[" constant-expression? "]" attribute-specifier-seq?'
)
@glrp.rule(
    'noptr-abstract-declarator : [split:continue_declarator_list] "(" begin-ptr-declarator ptr-abstract-declarator ")"'
)
@glrp.rule('noptr-abstract-declarator? : noptr-abstract-declarator')
@glrp.rule('noptr-abstract-declarator? : ')
@cxx98
def noptr_abstract_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('abstract-pack-declarator : noptr-abstract-pack-declarator [split:end_declarator_list]')
@glrp.rule('abstract-pack-declarator : ptr-operator abstract-pack-declarator')
@cxx11
def abstract_pack_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('noptr-abstract-pack-declarator : noptr-abstract-pack-declarator parameters-and-qualifiers')
@glrp.rule(
    'noptr-abstract-pack-declarator : noptr-abstract-pack-declarator "[" constant-expression? "]" attribute-specifier-seq?'
)
@glrp.rule('noptr-abstract-pack-declarator : [prec:left,0]"..."')
@cxx11
def noptr_abstract_pack_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-ptr-abstract-declarator : [split:ptr_abstract_declarator]')
@glrp.rule('begin-parameters-and-qualifiers : [split:parameters_and_qualifiers]')
@cxx98
def begin_abstract_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-type-id-declarator : [split:type_id_declarator]')
@glrp.rule('begin-type-id-no-declarator : [split:type_id_no_declarator]')
@glrp.rule('begin-type-id-abstract-declarator : [split:type_id_abstract_declarator]')
@cxx98
def begin_type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('abstract-declarator')
@cxx98_merge
def ambiguous_abstract_declarator_2(self, ambiguous_noptr_abstract_declarator, parameter_declaration_clause):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('abstract-declarator')
@cxx98_merge
def ambiguous_abstract_declarator(self, ptr_abstract_declarator, parameters_and_qualifiers):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('noptr-abstract-declarator')
@cxx98_merge
def ambiguous_noptr_abstract_declarator(self, ptr_declarator, parameter_declaration_clause):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('type-id')
@cxx98_merge
def ambiguous_type_id(self, continue_declarator_list, end_declarator_list):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('type-id')
@cxx98_merge
def ambiguous_type_id_2(self, type_specifier_seq_continue, type_specifier_seq_end):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('type-id')
@cxx98_merge
def ambiguous_type_id_3(self, ambiguous_noptr_abstract_declarator, parameter_declaration_clause):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('defining-type-id')
@cxx98_merge
def ambiguous_defining_type_id(self, continue_declarator_list, end_declarator_list):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('defining-type-id')
@cxx98_merge
def ambiguous_defining_type_id_2(self, defining_type_specifier_seq_continue, defining_type_specifier_seq_end):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('defining-type-id')
@cxx98_merge
def ambiguous_defining_type_id_3(self, ambiguous_noptr_abstract_declarator, parameter_declaration_clause):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser