from ..ir_ast import IrMetadataString, IrMetadataLink, IrMetadataNode, IrSpecializedMetadata, IrMetadataNull
from be_typing import TYPE_CHECKING


def p_ir_metadata_list(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-list : METADATA_NAME METADATA_REF ir-metadata-list
                         | empty
    """


def p_ir_metadata(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata : METADATA_NAME EQUAL ir-metadata-distinct ir-metadata-value
                    | METADATA_REF EQUAL ir-metadata-distinct ir-metadata-value
    """
    p[0] = None


def p_ir_metadata_distinct(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-distinct : DISTINCT
                             | empty
    """
    p[0] = None


def p_ir_metadata_value(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-value : ir-metadata-string
                          | ir-metadata-node
                          | ir-metadata-debug-node
                          | ir-metadata-ref
    """
    p[0] = p[1]


def p_ir_metadata_null(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-value : NULL
    """
    p[0] = IrMetadataNull()


def p_ir_metadata_ref(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-ref : METADATA_NAME
                        | METADATA_REF
    """
    p[0] = IrMetadataLink(p[1])


def p_ir_metadata_string(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-string : METADATA_MARK LITERAL_STRING
    """
    p[0] = IrMetadataString(p[2])


def p_ir_metadata_node(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-node : METADATA_MARK LBRACE ir-metadata-param-list RBRACE
    """
    p[0] = IrMetadataNode(p[3])


def p_ir_metadata_param_list(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-param-list : ir-metadata-param COMMA ir-metadata-param-list
    """
    p[0] = [p[1]] + p[3]


def p_ir_metadata_param_list_end(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-param-list : ir-metadata-param
                               | empty
    """
    p[0] = [p[1]] if p[1] is not None else []


def p_ir_metadata_param(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-param : ir-constant
                          | ir-metadata-value
    """
    p[0] = p[1]


def p_lex_disable_keywords(p):
    # type: (YaccProduction) -> None
    """
        lex-disable-keywords : empty
    """
    p.lexer.disable_keywords()


def p_lex_enable_keywords(p):
    # type: (YaccProduction) -> None
    """
        lex-enable-keywords : empty
    """
    p.lexer.enable_keywords()


def p_ir_metadata_debug_node(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-debug-node : METADATA_NAME LPAREN lex-disable-keywords LPAREN_MARK ir-metadata-debug-attribute-list RPAREN lex-enable-keywords
    """
    p[0] = IrSpecializedMetadata(p[1][1:], p[5])


def p_ir_metadata_debug_attribute_list(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-debug-attribute-list : ID_LABEL COLON ir-metadata-debug-attribute COMMA ir-metadata-debug-attribute-list
                                         | ID_LABEL COLON ir-metadata-debug-attribute
    """
    p[0] = [(p[1], p[3])]
    if len(p) > 4:
        p[0] += p[5]


def p_ir_metadata_debug_attribute_list_end(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-debug-attribute-list : empty
    """
    p[0] = []


def p_ir_metadata_debug_attribute(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-debug-attribute : LITERAL_STRING
                                    | LITERAL_DECIMAL
                                    | METADATA_NAME
                                    | METADATA_REF
                                    | NULL
                                    | ir-metadata-debug-flag-combination
    """
    p[0] = p[1]


def p_ir_metadata_debug_flag_combination(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-debug-flag-combination : ir-metadata-debug-flag PIPE ir-metadata-debug-flag-combination
                                           | ir-metadata-debug-flag
    """


def p_ir_metadata_debug_flag(p):
    # type: (YaccProduction) -> None
    """
        ir-metadata-debug-flag : ID_LABEL
    """


if TYPE_CHECKING:
    from ply.yacc import YaccProduction