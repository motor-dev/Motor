from be_typing import TYPE_CHECKING


def p_ir_instruction_list(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction-list : ir-instruction-list ir-instruction
    """
    p[0] = []


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
                       | LITERAL_DECIMAL COLON
    """
    p[0] = []


def p_ir_instruction(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction : ir-instruction-assignment ir-opcode
    """
    p[0] = []


def p_ir_instruction_assignment(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction-assignment : ID EQUAL 
                                  | empty
    """
    p[0] = []


def p_ir_instruction_metadata(p):
    # type: (YaccProduction) -> None
    """
        ir-instruction-attachment-list : COMMA METADATA_NAME METADATA_REF ir-instruction-attachment-list
                                       | empty
    """


if TYPE_CHECKING:
    from ply.yacc import YaccProduction