from .. import cl_ast


class Name:
    def __init__(self, lexer, name, position, target = None, targets = None, qualified = False,
                       dependent = False, resolved = True):
        self.lexer = lexer
        self.name = name
        self.position = position
        self.target = target
        self.targets = targets or (target,)
        self.qualified = qualified
        self.dependent = dependent
        self.resolved = resolved
        self.absolute = False

    def __add__(self, other):
        return Name(self.lexer,
                    self.name + other.name,
                    other.position,
                    target = other.target,
                    targets = self.targets + other.targets,
                    qualified = True,
                    dependent = self.dependent or other.dependent,
                    resolved = self.resolved and other.resolved)


def p_id(p):
    """
        namespace_id :                  NAMESPACE_ID
        namespace_id_shadow :           NAMESPACE_ID_SHADOW
        struct_id :                     STRUCT_ID
        struct_id_shadow :              STRUCT_ID_SHADOW
        typename_id :                   TYPENAME_ID
        typename_id_shadow :            TYPENAME_ID_SHADOW
        template_struct_id :            TEMPLATE_STRUCT_ID
        template_struct_id_shadow :     TEMPLATE_STRUCT_ID_SHADOW
        template_typename_id :          TEMPLATE_TYPENAME_ID
        template_typename_id_shadow :   TEMPLATE_TYPENAME_ID_SHADOW
        special_method_id :             SPECIAL_METHOD_ID
    """
    p[0] = Name(p.lexer, (p[1],), p.position(1),
                p.slice[1].found_object,
                qualified = not p.slice[1].type.endswith('SHADOW'),
                dependent = p.slice[1].type.find('TYPENAME'))


def p_template_new_template_id(p):
    """
        type_name_tpl_qualified : TEMPLATE ID template_arguments
                                | TEMPLATE NAMESPACE_ID template_arguments
                                | TEMPLATE VARIABLE_ID template_arguments
                                | TEMPLATE METHOD_ID template_arguments
                                | TEMPLATE STRUCT_ID template_arguments
                                | TEMPLATE TYPENAME_ID template_arguments
                                | TEMPLATE TEMPLATE_METHOD_ID template_arguments
                                | TEMPLATE TEMPLATE_STRUCT_ID template_arguments
                                | TEMPLATE TEMPLATE_TYPENAME_ID template_arguments
                                | TEMPLATE NAMESPACE_ID_SHADOW template_arguments
                                | TEMPLATE VARIABLE_ID_SHADOW template_arguments
                                | TEMPLATE METHOD_ID_SHADOW template_arguments
                                | TEMPLATE STRUCT_ID_SHADOW template_arguments
                                | TEMPLATE TYPENAME_ID_SHADOW template_arguments
                                | TEMPLATE TEMPLATE_METHOD_ID_SHADOW template_arguments
                                | TEMPLATE TEMPLATE_STRUCT_ID_SHADOW template_arguments
                                | TEMPLATE TEMPLATE_TYPENAME_ID_SHADOW template_arguments
    """
    p[0] = Name(p.lexer, (p[2],), p.position(2), resolved=False)
    # p.lexer.set_search_scope_ifn(p.slice[2].found_object.create_instance(p[2])) # TODO


def p_template_id(p):
    """
        struct_id : TEMPLATE_STRUCT_ID template_arguments
        struct_id_shadow : TEMPLATE_STRUCT_ID_SHADOW template_arguments
        typename_id : TEMPLATE_TYPENAME_ID template_arguments
        typename_id_shadow : TEMPLATE_TYPENAME_ID_SHADOW template_arguments
        object_name : TEMPLATE_METHOD_ID template_arguments
        object_name : TEMPLATE_METHOD_ID_SHADOW template_arguments
        object_name_id_qualified : TEMPLATE_METHOD_ID template_arguments
    """
    try:
        target = p.slice[1].found_object.create_instance(p[2])
    except cl_ast.templates.Template.InstanciationError as e:
        target = None
        p.lexer._error(e.msg, e.position)
        if e.error:
            p.lexer._note(e.error.message, e.error.position)
        p.lexer._note('template %s declared here' % p[1], p.slice[1].found_object.position)
    p[0] = Name(p.lexer, (p[1],), p.position(1), target,
                qualified = not p.slice[1].type.endswith('SHADOW'),
                resolved = (p.slice[1].type.find('TYPENAME') == -1))
    if target:
        p.lexer.set_search_scope_ifn(target)


def p_object_name_namespace(p):
    """
        object_name : namespace_id SCOPE object_name_qualified
                    | namespace_id_shadow SCOPE object_name_qualified
                    | struct_id SCOPE object_name_struct_qualified
                    | struct_id_shadow SCOPE object_name_struct_qualified
                    | typename_id SCOPE object_name_struct_qualified
                    | typename_id_shadow SCOPE object_name_struct_qualified
                    | template_typename_id SCOPE object_name_struct_qualified
                    | template_typename_id_shadow SCOPE object_name_struct_qualified
        type_name : namespace_id SCOPE type_name_qualified
                  | namespace_id_shadow SCOPE type_name_qualified
                  | struct_id SCOPE type_name_struct_qualified
                  | struct_id_shadow SCOPE type_name_struct_qualified
                  | typename_id SCOPE type_name_struct_qualified
                  | typename_id_shadow SCOPE type_name_struct_qualified
                  | template_typename_id SCOPE type_name_struct_qualified
                  | template_typename_id_shadow SCOPE type_name_struct_qualified
        special_method_name : namespace_id SCOPE special_method_name_qualified
                            | namespace_id_shadow SCOPE special_method_name_qualified
                            | struct_id SCOPE special_method_name_struct_qualified
                            | struct_id_shadow SCOPE special_method_name_struct_qualified
                            | typename_id SCOPE special_method_name_struct_qualified
                            | typename_id_shadow SCOPE special_method_name_struct_qualified
                            | template_typename_id SCOPE special_method_name_struct_qualified
                            | template_typename_id_shadow SCOPE special_method_name_struct_qualified
    """
    p[0] = p[1] + p[3]


def p_object_name_struct_qualified(p):
    """
        object_name_qualified : namespace_id SCOPE object_name_qualified
                              | object_name_struct_qualified
        object_name_struct_qualified : struct_id SCOPE object_name_struct_qualified
                                     | type_name_tpl_qualified SCOPE object_name_struct_qualified
                                     | object_name_id_qualified                                     %prec PRIO0

        type_name_qualified : namespace_id SCOPE type_name_qualified
                            | type_name_struct_qualified

        type_name_struct_qualified : struct_id SCOPE type_name_struct_qualified
                                   | type_name_tpl_qualified SCOPE type_name_struct_qualified
                                   | type_name_id_qualified                                         %prec PRIO0

        special_method_name_qualified : namespace_id SCOPE special_method_name_qualified
                                      | special_method_name_struct_qualified
        special_method_name_struct_qualified : struct_id SCOPE special_method_name_struct_qualified
                                     | type_name_tpl_qualified SCOPE special_method_name_struct_qualified
                                     | special_method_name_id_qualified                                     %prec PRIO0
    """
    if len(p) > 2:
        p[0] = p[1] + p[3]
    else:
        p[0] = p[1]


def p_object_name_namespace_root(p):
    """
        object_name : SCOPE object_name_qualified
        type_name : SCOPE type_name_qualified
        special_method_name : SCOPE special_method_name_qualified
    """
    p[0] = p[2]
    p[0].absolute = True


def p_object_name(p):
    """
        object_name : METHOD_ID                                                         %prec PRIO0
                    | VARIABLE_ID                                                       %prec PRIO0
                    | TEMPLATE_METHOD_ID                                                %prec PRIO0
                    | METHOD_ID_SHADOW                                                  %prec PRIO0
                    | VARIABLE_ID_SHADOW                                                %prec PRIO0
                    | TEMPLATE_METHOD_ID_SHADOW                                         %prec PRIO0

        object_name_id_qualified : METHOD_ID                                            %prec PRIO0
                                 | VARIABLE_ID                                          %prec PRIO0
                                 | TEMPLATE_METHOD_ID                                   %prec PRIO0
    """
    p[0] = Name(p.lexer, (p[1],), p.position(1), p.slice[1].found_object,
                qualified = not p.slice[1].type.endswith('SHADOW'))


def p_object_name_destructor(p):
    """
        special_method_name : NOT STRUCT_ID_SHADOW                                      %prec PRIO0
                            | NOT TEMPLATE_STRUCT_ID_SHADOW                             %prec PRIO0
        special_method_name_id_qualified : NOT STRUCT_ID_SHADOW                         %prec PRIO0
                                         | NOT TEMPLATE_STRUCT_ID_SHADOW                %prec PRIO0
    """
    owner = p.slice[2].found_object
    scope = p.lexer.scopes[-1]
    if owner != scope:
        p.lexer._error('declaration of ~%s as a member of %s' % (owner.name, scope.name), p.position(1))
        raise SyntaxError()
    if not owner.definition:
        p.lexer._error('invalid use of incomplete type %s' % owner.name, p.position(1))
        p.lexer._info('forward declaration of %s' % owner.name, owner.position)
        raise SyntaxError()
    p[0] = Name(p.lexer, (p[1]+p[2],), p.position(1), owner.definition.destructor,
                qualified = False)


def p_object_name_destructor_2(p):
    """
        special_method_name : NOT SPECIAL_METHOD_ID                                     %prec PRIO0
        special_method_name_id_qualified : NOT SPECIAL_METHOD_ID                        %prec PRIO0
    """
    owner = p.slice[2].found_object.owner
    if not owner.definition:
        p.lexer._error('invalid use of incomplete type %s' % owner.name, p.position(1))
        p.lexer._info('forward declaration of %s' % owner.name, owner.position)
        raise SyntaxError()
    p[0] = Name(p.lexer, (p[1]+p[2],), p.position(1), owner.definition.destructor,
                qualified = False)

def p_operator_name(p):
    """
        operator_name : OPERATOR PLUS
                      | OPERATOR MINUS
                      | OPERATOR TIMES
                      | OPERATOR DIVIDE
                      | OPERATOR MOD
                      | OPERATOR OR
                      | OPERATOR AND
                      | OPERATOR NOT
                      | OPERATOR XOR
                      | OPERATOR LSHIFT
                      | OPERATOR RSHIFT
                      | OPERATOR LOR
                      | OPERATOR LAND
                      | OPERATOR LNOT
                      | OPERATOR LT
                      | OPERATOR LE
                      | OPERATOR GT
                      | OPERATOR GE
                      | OPERATOR EQ
                      | OPERATOR NE
                      | OPERATOR EQUALS
                      | OPERATOR TIMESEQUAL
                      | OPERATOR DIVEQUAL
                      | OPERATOR MODEQUAL
                      | OPERATOR PLUSEQUAL
                      | OPERATOR MINUSEQUAL
                      | OPERATOR LSHIFTEQUAL
                      | OPERATOR RSHIFTEQUAL
                      | OPERATOR ANDEQUAL
                      | OPERATOR XOREQUAL
                      | OPERATOR OREQUAL
                      | OPERATOR PLUSPLUS
                      | OPERATOR MINUSMINUS
                      | OPERATOR ARROW
                      | OPERATOR LPAREN RPAREN
                      | OPERATOR LBRACKET RBRACKET
                      | OPERATOR PERIOD
                      | OPERATOR COMMA
    """
    p[0] = ('op%s' % p.slice[2].type.lower(), p.slice[2].found_object)
    p.set_position(0, 2)


def p_object_name_id(p):
    """
        object_name : ID                                                                %prec PRIO0
        object_name_id_qualified : ID                                                   %prec PRIO0
    """
    p[0] = Name(p.lexer, (p[1],), p.position(1), resolved = False)


def p_object_name_operator(p):
    """
        object_name : operator_name                                                     %prec PRIO0
        object_name_id_qualified : operator_name                                        %prec PRIO0
    """
    p[0] = Name(p.lexer, (p[1][0],), p.position(1), p[1][1],
                qualified = False,
                dependent = False)


def p_type_name(p):
    """
        type_name : struct_id                                                           %prec PRIO0
                  | typename_id                                                         %prec PRIO0
                  | template_struct_id                                                  %prec PRIO0
                  | template_typename_id                                                %prec PRIO0

        type_name_id_qualified : struct_id                                              %prec PRIO0
                               | typename_id                                            %prec PRIO0
                               | template_struct_id                                     %prec PRIO0
                               | template_typename_id                                   %prec PRIO0

        special_method_name : special_method_id                                         %prec PRIO0
        special_method_name_id_qualified : special_method_id                            %prec PRIO0
    """
    p[0] = p[1]


def p_type_name_shadow(p):
    """
        type_name : struct_id_shadow                                                    %prec PRIO0
                  | typename_id_shadow                                                  %prec PRIO0
                  | template_struct_id_shadow                                           %prec PRIO0
                  | template_typename_id_shadow                                         %prec PRIO0
    """
    p[0] = p[1]
