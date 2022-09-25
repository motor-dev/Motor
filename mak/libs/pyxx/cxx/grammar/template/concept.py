"""
concept-definition:
    concept concept-name = constraint-expression ;

concept-name:
    identifier
"""

import glrp
from ...parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('concept-definition : "concept" "identifier" "=" constraint-expression ";"')
@cxx20
def concept_definition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


#@glrp.rule('concept-name : "identifier"')
#@cxx20
#def concept_name_cxx20(self, p):
#    # type: (CxxParser, glrp.Production) -> Any
#    pass

if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser