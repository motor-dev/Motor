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


@glrp.rule('type-id : type-specifier-seq abstract-declarator?')
@cxx98
def type_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('type-id')
@cxx98_merge
def ambiguous_type_id(self, ambiguous_type_specifier):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    # Should never actually conflict as the precedence on '::' prevents option #2 from existing.
    # Used as rename.
    pass


@glrp.rule('defining-type-id : defining-type-specifier-seq abstract-declarator?')
@cxx98
def defining_type_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('abstract-declarator? : ptr-abstract-declarator')
@glrp.rule('abstract-declarator? : [split:declarator_end]')
@cxx98
def abstract_declarator_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('abstract-declarator? : parameters-and-qualifiers trailing-return-type')
@glrp.rule('abstract-declarator? : noptr-abstract-declarator parameters-and-qualifiers trailing-return-type')
#@glrp.rule('abstract-declarator? : abstract-pack-declarator')
@cxx11
def abstract_declarator_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('abstract-declarator?')
@cxx98_merge
def ambiguous_abstract_declarator_opt(self, ambiguous_noptr_abstract_declarator, parameters_and_qualifiers):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    # Should never actually conflict as the precedence on '::' prevents option #2 from existing.
    # Used as rename.
    pass


@glrp.rule('ptr-abstract-declarator : noptr-abstract-declarator[split:declarator_end]')
@glrp.rule('ptr-abstract-declarator : ptr-operator[split:declarator_end]')
@glrp.rule('ptr-abstract-declarator : ptr-operator ptr-abstract-declarator')
@cxx98
def ptr_abstract_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('noptr-abstract-declarator : parameters-and-qualifiers')
@glrp.rule('noptr-abstract-declarator : "[" constant-expression? "]" attribute-specifier-seq?')
@glrp.rule('noptr-abstract-declarator : noptr-abstract-declarator parameters-and-qualifiers')
@glrp.rule(
    'noptr-abstract-declarator : noptr-abstract-declarator "[" constant-expression? "]" attribute-specifier-seq?'
)
@glrp.rule(
    'noptr-abstract-declarator :  [split:declarator_continue]"(" noptr-abstract-declarator-disambiguation ptr-abstract-declarator ")"'
)
@cxx98
def noptr_abstract_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('noptr-abstract-declarator')
@cxx98_merge
def ambiguous_noptr_abstract_declarator(self, noptr_abstract_declarator, parameters_and_qualifiers):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.rule('noptr-abstract-declarator-disambiguation[split:noptr_abstract_declarator] :')
@cxx98
def noptr_abstract_declarator_disambiguation(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('abstract-pack-declarator : noptr-abstract-pack-declarator')
@glrp.rule('abstract-pack-declarator : ptr-operator abstract-pack-declarator')
@cxx11
def abstract_pack_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('noptr-abstract-pack-declarator : noptr-abstract-pack-declarator parameters-and-qualifiers')
@glrp.rule(
    'noptr-abstract-pack-declarator : noptr-abstract-pack-declarator "[" constant-expression? "]" attribute-specifier-seq?'
)
@glrp.rule('noptr-abstract-pack-declarator : [split:pack_declarator]"..."')
@cxx11
def noptr_abstract_pack_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ....parser import CxxParser