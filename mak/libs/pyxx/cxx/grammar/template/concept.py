"""
concept-definition:
    concept concept-name = constraint-expression ;

concept-name:
    identifier
"""

import glrp
from ...parse import cxx20
from ....ast.declarations import ConceptDefinition
from motor_typing import TYPE_CHECKING


@glrp.rule('concept-definition : "concept" "identifier" "=" constraint-expression ";"')
@cxx20
def concept_definition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ConceptDefinition(p[1].text(), p[3])


#@glrp.rule('concept-name : "identifier"')
#@cxx20
#def concept_name_cxx20(self, p):
#    # type: (CxxParser, glrp.Production) -> Any
#    pass

if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser