from ..ir_ast import IrReference
from ..ir_ast.instructions import IrInstLabel
from ..ir_ast import IrMetadataLink
from motor_typing import TYPE_CHECKING


def p_ir_instruction_list(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction-list : ir-instruction-list ir-instruction
    """
    p[0] = p[1]
    if p[2] is not None:
        p[0].append(p[2])


def p_ir_instruction_list_end(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction-list : empty
    """
    p[0] = []


def p_ir_instruction_label(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction : ID_LABEL COLON
                       | ir-literal-decimal COLON
    """
    p[0] = IrInstLabel(str(p[1]), [])


def p_ir_instruction(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction : ir-opcode
    """
    p[0] = p[1]


def p_ir_instruction_assignment(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction-assignment : ID EQUAL 
    """
    p[0] = IrReference(p[1])


def p_ir_instruction_assignment_opt(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction-assignment-opt : ir-instruction-assignment
                                      | empty
    """
    p[0] = p[1]


def p_ir_instruction_metadata(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction-attachment-list : COMMA METADATA_NAME METADATA_REF ir-instruction-attachment-list
    """
    p[0] = [(IrMetadataLink(p[2]), IrMetadataLink(p[3]))] + p[4]


def p_ir_instruction_metadata_empty(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction-attachment-list : empty
    """
    p[0] = []


if TYPE_CHECKING:
    from ply.yacc import YaccProduction