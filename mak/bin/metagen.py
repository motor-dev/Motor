import os
import sys
import re
from typing import Dict, Optional, Tuple, Any, List, BinaryIO, TextIO
import pickle

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'vendor'))
import pyxx
import glrp
from pyxx import ast, utils, messages


@messages.error
def m0000(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """unknown attribute motor::{attribute}"""
    return locals()


@messages.error
def m0001(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """unknown meta attribute {attribute}"""
    return locals()


@messages.error
def m0002(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """trailing tokens after attribute {attribute}"""
    return locals()


@messages.error
def m0003(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """invalid value for attribute {attribute}"""
    return locals()


@messages.warning('ignored-attribute', True)
def m0004(logger: messages.Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """motor attribute ignored"""
    return locals()


@messages.warning('ignored-attribute', True)
def m0005(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """motor attribute {attribute} ignored due to export directive"""
    return locals()


@messages.diagnostic
def m0006(logger: messages.Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """export directive here"""
    return locals()


@messages.warning('ignored-attribute', True)
def m0007(logger: messages.Logger, position: Tuple[int, int], attribute: str, object_type: str) -> Dict[str, Any]:
    """motor attribute {attribute} ignored on object of type {object_type}"""
    return locals()


@messages.error
def m0010(logger: messages.Logger, position: Tuple[int, int], export: str) -> Dict[str, Any]:
    """invalid value {export} for export attribute"""
    return locals()


@messages.warning('multiple-attribute', True)
def m0011(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """multiple definitions for attribute {attribute}"""
    return locals()


@messages.diagnostic
def m0012(logger: messages.Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """previous definition here"""
    return locals()


@messages.error
def m0100(logger: messages.Logger, position: Tuple[int, int], entity_name: str, namespace_name: str) -> Dict[str, Any]:
    """Cannot declare object {entity_name} here, as the definition of {namespace_name} is not visible in this translation unit"""
    return locals()


@messages.error
def m0101(logger: messages.Logger, position: Tuple[int, int], entity_name: str, namespace_name: str) -> Dict[str, Any]:
    """Object {entity_name} does not exist in {namespace_name}, or has been declared outside of this translation unit"""
    return locals()


@messages.error
def m0102(logger: messages.Logger, position: Tuple[int, int], entity_name: str) -> Dict[str, Any]:
    """redefinition of {entity_name}"""
    return locals()


@messages.error
def m0103(logger: messages.Logger, position: Tuple[int, int], entity_name: str) -> Dict[str, Any]:
    """{entity_name} is explicitely marked as exported but cannot be exported."""
    return locals()


@messages.warning('implicit-export', True)
def m0104(logger: messages.Logger, position: Tuple[int, int], entity_name: str) -> Dict[str, Any]:
    """{entity_name} is implicitely marked as exported but cannot be exported."""
    return locals()


@messages.error
def m0200(logger: messages.Logger, position: Tuple[int, int], include_name: str) -> Dict[str, Any]:
    """Meta file needs to #include {include_name}"""
    return locals()


@messages.error
def m0300(logger: messages.Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """Extraneous template parameter list in template specialization or out-of-line template definition"""
    return locals()


class NotFoundException(Exception):
    pass


class NotDefinedException(Exception):
    pass


class NotExportedException(Exception):
    pass


class IgnoredException(Exception):
    pass


class Attributes(object):
    def __init__(self) -> None:
        self.export = None  # type: Optional[Tuple[Tuple[int, int], bool]]
        self.documentation = []  # type: List[Tuple[Tuple[int, int], str]]
        self.interfaces = []  # type: List[Tuple[Tuple[int, int], str]]
        self.name = None  # type: Optional[Tuple[Tuple[int, int], str]]
        self.alias = []  # type: List[Tuple[Tuple[int, int], str]]
        self.tags = []  # type: List[Tuple[Tuple[int, int], List[glrp.Token]]]

    def exported(self) -> bool:
        return self.export is None or self.export[1]


class Template(object):
    def __init__(self) -> None:
        self._parameters = []


class MetaObject(object):

    def __init__(self, position: Tuple[int, int], attributes: Attributes, parent: Optional["MetaObject"]) -> None:
        self._attributes = attributes
        self._parent = parent if parent is not None else self
        self._children = {}  # type: Dict[str, MetaObject]
        if parent is None:
            self._namespace = ([], [])  # type: Tuple[List[str], List[str]]
        else:
            self._namespace = (parent._namespace[0][:], parent._namespace[1][:])
        self._objects = []  # type: List[MetaObject]
        self._declared_objects = {}  # type: Dict[str, Tuple[bool, Attributes]]
        self.position = position

    def file_name(self) -> str:
        return self._parent.file_name()

    def dump_exports(self, namespace: List[str], out_namespace: BinaryIO) -> None:
        for name, child in self._children.items():
            namespace.append(name)
            child.dump_exports(namespace, out_namespace)
            namespace.pop(-1)

    def write_declarations(self, namespace: List[str], out_cc: TextIO, out_hh: TextIO) -> None:
        for name, child in self._children.items():
            namespace.append(name)
            child.write_declarations(namespace, out_cc, out_hh)
            namespace.pop(-1)

    def _write_object_names(self, object_names: List[Tuple[str, str]], owner: str, out: TextIO) -> str:
        file_name = self.file_name()
        out.write('MOTOR_EXPORT ::Motor::Meta::Object s_%s_objects[%d] = {\n' % (file_name, len(object_names)))
        object_count = len(object_names)
        i = 0
        for object_name, object_value in object_names:
            if i < object_count - 1:
                next_objects = '{&s_%s_objects[%d]}' % (file_name, i + 1)
                comma = ','
            else:
                next_objects = '{%s->objects.exchange(s_%s_objects)}' % (owner, file_name)
                comma = ''
            out.write('    {\n'
                      '        %s,\n'
                      '        %s,\n'
                      '        %s,\n'
                      '        ::Motor::Meta::Value(%s)\n'
                      '    }%s\n' % (next_objects, owner, object_name, object_value, comma))
            i += 1
        out.write('};\n')
        return '{s_%s_objects}' % file_name

    def write_metaclasses(self, namespace: List[str], out_cc: TextIO, out_hh: TextIO) -> None:
        object_names = []
        for name, child in self._children.items():
            namespace.append(name)
            child.write_metaclasses(namespace, out_cc, out_hh)
            o = child.object_name()
            if o is not None:
                object_names.append(o)
            namespace.pop(-1)
        if object_names:
            if namespace:
                out_cc.write('\nnamespace %s\n'
                             '{\n'
                             '\n' % (' { namespace '.join(namespace)))
            self._write_object_names(object_names, self._parent.name(), out_cc)
            if namespace:
                out_cc.write('%s\n' % ('}' * len(namespace)))

    def object_name(self) -> Optional[Tuple[str, str]]:
        return None

    def name(self) -> str:
        raise NotImplementedError

    def cpp_name(self) -> str:
        raise NotImplementedError

    def get_child(self, child_name: str) -> "MetaObject":
        return self._children[child_name]

    def add_declared_object(self, name: str, exported: bool, attributes: Attributes) -> None:
        self._declared_objects[name] = (exported, attributes)

    def get_exported_object(self, name: str) -> Tuple[bool, Attributes]:
        return self._declared_objects[name]

    def add_using_declaration(self, namespace: str, name: str) -> None:
        print(namespace, name)


class RootNamespace(MetaObject):
    def __init__(self, file_name: str, module_name: str):
        super().__init__((0, 0), Attributes(), None)
        self._file_name = file_name
        self._cpp_name = 'motor_%s_Namespace' % module_name

    def cpp_name(self) -> str:
        return self._cpp_name

    def file_name(self) -> str:
        return self._file_name

    def name(self) -> str:
        return '::Motor::' + self._cpp_name + '()'

    def write_declarations(self, namespace: List[str], out_cc: TextIO, out_hh: TextIO) -> None:
        out_hh.write('namespace Motor\n{\n\nraw<Meta::Class> %s();\n' % self._cpp_name)
        super().write_declarations(namespace, out_cc, out_hh)
        out_hh.write('\n}\n')


class Namespace(MetaObject):

    def __init__(self, position: Tuple[int, int], attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(position, attributes, parent)
        self._name = name
        self._cpp_name = parent.cpp_name() + '_' + name
        parent._children[name] = self
        self._namespace[0].append(name)
        assert pyxx.logger is not None
        for position, interface in attributes.interfaces:
            m0007(pyxx.logger, position, 'interface', 'namespace')

    def cpp_name(self) -> str:
        return self._cpp_name

    def dump_exports(self, namespace: List[str], out_namespace: BinaryIO) -> None:
        pickle.dump(namespace, out_namespace)
        super().dump_exports(namespace, out_namespace)

    def write_declarations(self, namespace: List[str], out_cc: TextIO, out_hh: TextIO) -> None:
        out_hh.write('raw<Meta::Class> %s();\n' % self._cpp_name)
        super().write_declarations(namespace, out_cc, out_hh)

    def name(self) -> str:
        return '::Motor::' + self._cpp_name + '()'


class Class(MetaObject):

    def __init__(
            self,
            position: Tuple[int, int],
            attributes: Attributes,
            name: str,
            is_value_type: bool,
            superclass: Optional[str],
            parent: MetaObject
    ):
        super().__init__(position, attributes, parent)
        self._name = name
        parent._children[name] = self
        self._superclass = superclass if superclass is not None else 'void'
        self._namespace[1].append(name)
        self._is_value_type = is_value_type

    def name(self) -> str:
        return 'motor_class<::%s>()' % '::'.join(self._namespace[0] + self._namespace[1])

    def object_name(self) -> Tuple[str, str]:
        return (
            '::Motor::Meta::ClassID< %s >::name()' % self._name,
            '::Motor::Meta::ClassID< %s >::klass()' % self._name
        )

    def write_declarations(self, namespace: List[str], out_cc: TextIO, out_hh: TextIO) -> None:
        out_hh.write(
            '\nnamespace Meta\n'
            '{\n\n'
            'MOTOR_DECLARE_CLASS_ID(::%s)\n\n'
            '}\n\n' % '::'.join(namespace))
        out_cc.write(
            '\nnamespace Motor { namespace Meta\n'
            '{\n\n'
            'template<>\nistring ClassID<::%(cpp_name)s>::name()\n'
            '{\n'
            '    static istring s_name("%(name)s");\n'
            '    return s_name;\n'
            '}\n\n'
            'template<>\nconst Class ClassID<::%(cpp_name)s>::s_class = {\n'
            '};\n\n'
            '}}\n\n'
            '' % {'cpp_name': '::'.join(namespace), 'name': self._name}
        )
        super().write_declarations(namespace, out_cc, out_hh)

    def write_metaclasses(self, namespace: List[str], out_cc: TextIO, out_hh: TextIO) -> None:
        pass


class Enum(Class):
    def __init__(self, position: Tuple[int, int], attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(position, attributes, name, True, None, parent)


class Parameter(object):
    def __init__(self) -> None:
        pass


class Overload(object):
    def __init__(self) -> None:
        self._parameters = []  # type: List[Overload]


class Method(MetaObject):
    def __init__(self, position: Tuple[int, int], attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(position, attributes, parent)
        self._name = name
        self._overloads = []  # type: List[Overload]


class Variable(MetaObject):
    def __init__(self, position: Tuple[int, int], attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(position, attributes, parent)
        self._name = name
        self._type = ()


class TypeDef(MetaObject):
    def __init__(self, position: Tuple[int, int], attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(position, attributes, parent)
        self._name = name


class BaseClauseVisitor(ast.Visitor):
    def __init__(self, is_default_public: bool):
        self.base_clause = None  # type: Optional[str]
        self._is_default_public = is_default_public
        self._is_public = self._is_default_public

    def visit_ambiguous_base_clause(self, ambiguous_base_clause: ast.AmbiguousBaseClause) -> None:
        ambiguous_base_clause.accept_first_base_clause(self)

    def visit_base_clause(self, base_clause: ast.BaseClause) -> None:
        base_clause.accept_base_specifiers(self)

    def visit_base_specifier(self, base_specifier: ast.BaseSpecifier) -> None:
        base_specifier.accept_access_specifier(self)
        if self._is_public and self.base_clause is None:
            sref = utils.StringRef()
            base_specifier.accept_base_type(sref)
            self.base_clause = sref.result

    def visit_access_specifier_default(self, access_specifier: ast.AccessSpecifierDefault) -> None:
        self._is_public = self._is_default_public

    def visit_access_specifier_public(self, access_specifier: ast.AccessSpecifierPublic) -> None:
        self._is_public = True

    def visit_access_specifier_protected(self, access_specifier: ast.AccessSpecifierProtected) -> None:
        self._is_public = False

    def visit_access_specifier_private(self, access_specifier: ast.AccessSpecifierPrivate) -> None:
        self._is_public = False

    def visit_access_specifier_macro(self, access_specifier: ast.AccessSpecifierMacro) -> None:
        self._is_public = False


class AttributeParser(ast.Visitor):
    def __init__(self) -> None:
        self.attributes = Attributes()

    def parse_meta_attributes(self, tokens: List[glrp.Token]) -> None:
        assert pyxx.logger is not None
        tokens = tokens[:]

        def skip(token_list: List[glrp.Token]) -> None:
            nested_depth = 0
            while tokens:
                skipped_token = token_list.pop(0).text()
                if skipped_token == ',' and nested_depth == 0:
                    break
                elif skipped_token in ('(', '[', '{'):
                    nested_depth += 1
                elif skipped_token in (')', ']', '}'):
                    nested_depth -= 1

        while tokens:
            attribute_token = tokens.pop(0)
            attribute = attribute_token.text()
            if attribute == 'noexport':
                if self.attributes.export is not None:
                    if m0011(pyxx.logger, attribute_token.position, 'export'):
                        m0012(pyxx.logger, self.attributes.export[0])
                self.attributes.export = (attribute_token.position, False)
            elif attribute == 'export':
                if self.attributes.export is not None:
                    if m0011(pyxx.logger, attribute_token.position, 'export'):
                        m0012(pyxx.logger, self.attributes.export[0])
                if len(tokens) > 1 and tokens[0].text() == '=':
                    tokens.pop(0)
                    export_token = tokens.pop(0)
                    export = export_token.text()
                    if export in ('yes', 'true', '1'):
                        self.attributes.export = (attribute_token.position, True)
                    elif export in ('no', 'false', '0'):
                        self.attributes.export = (attribute_token.position, False)
                    else:
                        m0010(pyxx.logger, export_token.position, export)
                else:
                    self.attributes.export = (attribute_token.position, True)
            elif attribute == 'name':
                if self.attributes.name is not None:
                    if m0011(pyxx.logger, attribute_token.position, attribute):
                        m0012(pyxx.logger, self.attributes.name[0])
                elif len(tokens) < 2 or tokens[0].text() != '=':
                    m0003(pyxx.logger, attribute_token.position, attribute)
                    skip(tokens)
                else:
                    tokens.pop(0)
                    self.attributes.name = (attribute_token.position, tokens.pop(0).text())
            elif attribute == 'alias':
                if len(tokens) < 2 or tokens[0].text() != '=':
                    m0003(pyxx.logger, attribute_token.position, attribute)
                    skip(tokens)
                else:
                    tokens.pop(0)
                    self.attributes.alias.append((attribute_token.position, tokens.pop(0).text()))
            elif attribute == 'tag':
                if len(tokens) < 2 or tokens[0].text() != '=':
                    m0003(pyxx.logger, attribute_token.position, attribute)
                    skip(tokens)
                else:
                    tokens.pop(0)
                    tag = []  # type: List[glrp.Token]
                    self.attributes.tags.append((attribute_token.position, tag))
                    depth = 0
                    while tokens:
                        token = tokens[0].text()
                        if token == ',' and depth == 0:
                            break
                        tag.append(tokens.pop(0))
                        if token in ('(', '[', '{'):
                            depth += 1
                        elif token in (')', ']', '}'):
                            depth -= 1
            elif attribute == 'interface':
                if len(tokens) < 2 or tokens[0].text() != '=':
                    m0003(pyxx.logger, attribute_token.position, attribute)
                    skip(tokens)
                else:
                    tokens.pop(0)
                    self.attributes.interfaces.append((attribute_token.position, tokens.pop(0).text()))

            else:
                m0001(pyxx.logger, attribute_token.position, attribute)
                skip(tokens)
            if tokens:
                if tokens[0].text() == ',':
                    tokens.pop(0)
                    continue
                else:
                    m0002(pyxx.logger, tokens[0].position, attribute)
                    skip(tokens)
        if not self.attributes.exported():
            assert self.attributes.export is not None
            show_position = False
            for position, _ in self.attributes.documentation:
                show_position |= m0005(pyxx.logger, position, 'documentation')
            for position, _ in self.attributes.interfaces:
                show_position |= m0005(pyxx.logger, position, 'interface')
            if self.attributes.name is not None:
                show_position |= m0005(pyxx.logger, self.attributes.name[0], 'name')
            for position, _ in self.attributes.alias:
                show_position |= m0005(pyxx.logger, position, 'alias')
            for position, _ in self.attributes.tags:
                show_position |= m0005(pyxx.logger, position, 'tag')
            if show_position:
                m0006(pyxx.logger, self.attributes.export[0])

    def visit_attribute_named_list(self, attribute_named_list: ast.AttributeNamedList) -> None:
        attribute_named_list.accept_attributes(self)

    def visit_attribute_named(self, using_namespace: Optional[str], attribute_named: ast.AttributeNamed) -> None:
        if using_namespace != 'motor' and attribute_named.namespace != 'motor':
            return
        if attribute_named.attribute != 'meta':
            assert pyxx.logger is not None
            m0000(pyxx.logger, attribute_named.position, attribute_named.attribute)
            return
        if attribute_named.value is None:
            return
        self.parse_meta_attributes(attribute_named.value)

    def visit_attribute_macro(self, attribute_macro: ast.AttributeMacro) -> None:
        if attribute_macro.attribute != 'motor_meta':
            return
        if attribute_macro.values:
            if attribute_macro.values[0].text() == '(':
                self.parse_meta_attributes(attribute_macro.values[1:-1])
            else:
                self.parse_meta_attributes(attribute_macro.values)


class NameParser(ast.Visitor):
    def __init__(self, namespace: MetaObject):
        self.position = (0, 0)
        self.namespace = namespace  # type: MetaObject
        self.object = namespace  # type: Optional[MetaObject]
        self.namespace_name = 'the enclosing namespace'
        self.name = ''
        self.identifier = ''
        self.qualified = False

    def visit_declarator_list(self, declarator_list: ast.DeclaratorList) -> None:
        declarator_list.accept_element(self)

    # these should not happen as they are only valid for method parameter declarations
    def visit_declarator_element_abstract(self, declarator_element_abstract: ast.DeclaratorElementAbstract) -> None:
        raise NotImplementedError

    # these should not happen as they are only valid for template parameter declarations
    def visit_declarator_element_abstract_pack(self,
                                               declarator_element_abstract_pack: ast.DeclaratorElementAbstractPack) -> None:
        raise NotImplementedError

    def visit_declarator_element_pack_id(self, declarator_element_pack_id: ast.DeclaratorElementPackId) -> None:
        raise NotImplementedError

    def visit_declarator_element_id(self, declarator_element_id: ast.DeclaratorElementId) -> None:
        declarator_element_id.accept_name(self)

    def visit_declarator_element_group(self, declarator_element_group: ast.DeclaratorElementGroup) -> None:
        declarator_element_group.accept_next(self)

    def visit_declarator_element_pointer(self, declarator_element_pointer: ast.DeclaratorElementPointer) -> None:
        declarator_element_pointer.accept_next(self)

    def visit_declarator_element_reference(self, declarator_element_reference: ast.DeclaratorElementReference) -> None:
        declarator_element_reference.accept_next(self)

    def visit_declarator_element_rvalue_reference(self,
                                                  declarator_element_rvalue_reference: ast.DeclaratorElementRValueReference) -> None:
        declarator_element_rvalue_reference.accept_next(self)

    def visit_declarator_element_array(self, declarator_element_array: ast.DeclaratorElementArray) -> None:
        declarator_element_array.accept_next(self)

    def visit_declarator_element_method(self, declarator_element_method: ast.DeclaratorElementMethod) -> None:
        declarator_element_method.accept_next(self)

    def visit_reference(self, ref: ast.Reference) -> None:
        self.position = ref.position
        if len(ref.name_list) > 1:
            self.qualified = True
            for id in ref.name_list[:-1]:
                if self.object is None:
                    sr = utils.StringRef()
                    id.accept(sr)
                    self.name += sr.result
                    raise NotDefinedException()
                self.namespace = self.object
                id.accept(self)
                self.namespace_name = self.name
                self.name += '::'
        if self.object is None:
            sr = utils.StringRef()
            ref.name_list[-1].accept(sr)
            self.name += sr.result
            raise NotDefinedException()
        ref.name_list[-1].accept(self)

    def visit_root_id(self, root_id: ast.RootId) -> None:
        self.name += '::'
        self.object = self.namespace
        while self.object._parent != self.object:
            self.object = self.object._parent

    def visit_id(self, identifier: ast.Id) -> None:
        self.name += identifier.name
        self.identifier = identifier.name
        try:
            self.object = self.namespace.get_child(identifier.name)
        except KeyError:
            self.object = None
            try:
                self.namespace.get_exported_object(identifier.name)
            except KeyError:
                if self.qualified:
                    raise NotFoundException()

    def visit_template_id(self, template_id: ast.TemplateId) -> None:
        template_id.accept_id(self)

    def visit_destructor_id(self, destructor_id: ast.DestructorId) -> None:
        visitor = pyxx.utils.StringRef()
        destructor_id.accept(visitor)
        self.name += visitor.result
        self.identifier = visitor.result
        raise IgnoredException()

    def visit_operator_id(self, operator_id: ast.OperatorId) -> None:
        visitor = pyxx.utils.StringRef()
        operator_id.accept(visitor)
        self.name += visitor.result
        self.identifier = visitor.result
        raise NotExportedException()

    def visit_conversion_operator_id(self, conversion_operator_id: ast.ConversionOperatorId) -> None:
        visitor = pyxx.utils.StringRef()
        conversion_operator_id.accept(visitor)
        self.name += visitor.result
        self.identifier = visitor.result
        raise NotExportedException()

    def visit_literal_operator_id(self, literal_operator_id: ast.LiteralOperatorId) -> None:
        visitor = pyxx.utils.StringRef()
        literal_operator_id.accept(visitor)
        self.name += visitor.result
        self.identifier = visitor.result
        raise NotExportedException()


class DeclarationVisitor(ast.Visitor):
    def __init__(self, template_stack: List[Template], attributes: Attributes, namespace: MetaObject):
        super().__init__()
        self._template_stack = template_stack
        self._attributes = attributes
        self._namespace = namespace
        self._static = False

    def visit_decl_specifier_seq(self, decl_specifier_seq: ast.DeclSpecifierSeq) -> None:
        decl_specifier_seq.accept_decl_specifiers(self)

    def visit_declaration_specifier(self, declaration_specifier: ast.DeclarationSpecifier) -> None:
        pass

    def visit_storage_class_specifier(self, storage_class_specifier: ast.StorageClassSpecifier) -> None:
        if storage_class_specifier.decl_specifier == 'static':
            self._static = True

    def visit_init_declarator_list(self, init_declarator_list: ast.InitDeclaratorList) -> None:
        for _, init_declarator in init_declarator_list.init_declarators:
            init_declarator.accept(self)

    def visit_init_declarator(self, init_declarator: ast.InitDeclarator) -> None:
        init_declarator.accept_declarator(self)

    def visit_member_init_declarator(self, member_init_declarator: ast.MemberInitDeclarator) -> None:
        member_init_declarator.accept_declarator(self)

    def visit_declarator_list(self, declarator_list: ast.DeclaratorList) -> None:
        assert pyxx.logger is not None
        visitor = NameParser(self._namespace)
        try:
            declarator_list.accept(visitor)
        except NotExportedException as e:
            if self._attributes.export:
                m0103(pyxx.logger, visitor.position, visitor.name)
            else:
                m0104(pyxx.logger, visitor.position, visitor.name)
        except IgnoredException as e:
            if self._attributes.export:
                m0103(pyxx.logger, visitor.position, visitor.name)
        except NotFoundException:
            m0101(pyxx.logger, visitor.position, visitor.name, visitor.namespace_name)
        except NotDefinedException:
            m0100(pyxx.logger, visitor.position, visitor.name, visitor.namespace_name)
        else:
            # methods and variables are exported when declared in their namespace/container
            if not visitor.qualified:
                if self._template_stack:
                    # cannot eport template methods/variables.
                    if self._attributes.exported():
                        m0103(pyxx.logger, visitor.position, visitor.name)
                    else:
                        m0104(pyxx.logger, visitor.position, visitor.name)
                else:
                    print(visitor.identifier)
                    if declarator_list.is_method():
                        pass


class Explorer(utils.RecursiveVisitor):

    def __init__(self, file_name: str, module_name: str):
        self.namespace = RootNamespace(file_name, module_name)  # type: MetaObject
        self._access_specifier = []  # type: List[str]
        self._publish = [True]
        self._template_stack = []  # type: List[Template]

    def visit_attribute_named(self, using_namespace: Optional[str], attribute_named: ast.AttributeNamed) -> None:
        assert pyxx.logger is not None
        if using_namespace != 'motor' and attribute_named.namespace != 'motor':
            return
        if attribute_named.attribute != 'meta':
            m0000(pyxx.logger, attribute_named.position, attribute_named.attribute)
            return
        if attribute_named.value is None:
            return
        m0004(pyxx.logger, attribute_named.position)

    def visit_attribute_macro(self, attribute_macro: ast.AttributeMacro) -> None:
        assert pyxx.logger is not None
        if attribute_macro.attribute != 'motor_meta':
            return
        m0004(pyxx.logger, attribute_macro.position)

    def visit_compound_statement(self, compound_statement: ast.CompoundStatement) -> None:
        self._publish.append(False)
        super().visit_compound_statement(compound_statement)
        self._publish.pop(-1)

    def visit_namespace_declaration(self, namespace_declaration: ast.NamespaceDeclaration) -> None:
        if self._publish[-1]:
            if namespace_declaration.namespace_name is not None:
                attribute_parser = AttributeParser()
                namespace_declaration.accept_attributes(attribute_parser)
                if attribute_parser.attributes.exported():
                    namespace = self.namespace
                    for _, name in namespace_declaration.nested_name:
                        try:
                            self.namespace = self.namespace.get_child(name)
                        except KeyError:
                            self.namespace = Namespace(namespace_declaration.position, Attributes(), name,
                                                       self.namespace)
                    try:
                        self.namespace = self.namespace.get_child(namespace_declaration.namespace_name)
                    except KeyError:
                        self.namespace = Namespace(namespace_declaration.position, attribute_parser.attributes,
                                                   namespace_declaration.namespace_name, self.namespace)
                    namespace_declaration.accept_children(self)
                    self.namespace = namespace
                else:
                    self._publish.append(False)
                    namespace_declaration.accept_children(self)
                    self._publish.pop(-1)
            else:
                self._publish.append(False)
                super().visit_namespace_declaration(namespace_declaration)
                self._publish.pop(-1)
        else:
            super().visit_namespace_declaration(namespace_declaration)

    def visit_simple_declaration(self, simple_declaration: ast.SimpleDeclaration) -> None:
        if self._publish[-1]:
            attribute_parser = AttributeParser()
            simple_declaration.accept_attributes(attribute_parser)
            if attribute_parser.attributes.exported():
                # look for class definitions in the decl-specifier-seq
                simple_declaration.accept_decl_specifier_seq(self)

                # also export declaration itself
                visitor = DeclarationVisitor(self._template_stack, attribute_parser.attributes, self.namespace)
                simple_declaration.accept_decl_specifier_seq(visitor)
                simple_declaration.accept_init_declarator_list(visitor)
                simple_declaration.accept_init_declarator_list(self)
            else:
                self._publish.append(False)
                simple_declaration.accept_decl_specifier_seq(self)
                simple_declaration.accept_init_declarator_list(self)
                self._publish.pop(-1)
        else:
            super().visit_simple_declaration(simple_declaration)

    def visit_declarator_element_method(self, declarator_element_method: ast.DeclaratorElementMethod) -> None:
        if not self._publish[-1]:
            super().visit_declarator_element_method(declarator_element_method)

    def visit_class_specifier(self, class_specifier: ast.ClassSpecifier) -> None:
        assert pyxx.logger is not None
        if self._publish[-1]:
            if class_specifier.name is not None:
                attributes_parser = AttributeParser()
                class_specifier.accept_attributes(attributes_parser)
                if attributes_parser.attributes.exported():
                    base_clause_visitor = BaseClauseVisitor(class_specifier.class_type != 'class')
                    class_specifier.accept_base_clause(base_clause_visitor)
                    namespace = self.namespace
                    index = 0
                    partial_name = ''
                    if class_specifier.name.is_absolute():
                        index = 1
                        partial_name = '::'
                        while self.namespace != self.namespace._parent:
                            self.namespace = self.namespace._parent
                    for name in class_specifier.name.name_list[index:-1]:
                        sr = utils.StringRef()
                        name.accept(sr)
                        partial_name += sr.result + '::'
                        try:
                            self.namespace = self.namespace.get_child(sr.result)
                        except KeyError:
                            sr = utils.StringRef()
                            class_specifier.name.accept(sr)
                            m0100(pyxx.logger, class_specifier.name.position, sr.result, partial_name[:-2])
                            break
                    else:
                        sr = utils.StringRef()
                        class_specifier.name.name_list[-1].accept(sr)
                        try:
                            self.namespace = self.namespace.get_child(sr.result)
                        except KeyError:
                            try:
                                exported, attributes = self.namespace.get_exported_object(sr.result)
                            except KeyError:
                                if len(class_specifier.name.name_list) > 1:
                                    m0101(pyxx.logger, class_specifier.name.position, sr.result, partial_name[:-2])
                                else:
                                    self.namespace = Class(class_specifier.position, attributes_parser.attributes,
                                                           sr.result, class_specifier.class_type != 'class',
                                                           base_clause_visitor.base_clause, self.namespace)
                            else:
                                if exported:
                                    self.namespace = Class(class_specifier.position, attributes_parser.attributes,
                                                           sr.result, class_specifier.class_type != 'class',
                                                           base_clause_visitor.base_clause, self.namespace)
                                else:
                                    self._publish.append(False)
                                    class_specifier.accept_name(self)
                                    self._access_specifier.append(
                                        class_specifier.class_type in ('struct', 'union') and 'public' or 'private')
                                    class_specifier.accept_base_clause(self)
                                    self._access_specifier.pop(-1)
                                    class_specifier.accept_members(self)
                                    self._publish.pop(-1)

                        else:
                            m0102(pyxx.logger, class_specifier.position, sr.result)
                            m0012(pyxx.logger, self.namespace.position)
                        self._access_specifier.append(
                            class_specifier.class_type in ('struct', 'union') and 'public' or 'private')
                        class_specifier.accept_members(self)
                        self._access_specifier.pop(-1)
                        self.namespace = namespace
                else:
                    self._publish.append(False)
                    class_specifier.accept_name(self)
                    class_specifier.accept_base_clause(self)
                    class_specifier.accept_members(self)
                    self._publish.pop(-1)
            else:
                self._publish.append(False)
                super().visit_class_specifier(class_specifier)
                self._publish.pop(-1)
        else:
            super().visit_class_specifier(class_specifier)

    def visit_enum_specifier(self, enum_specifier: ast.EnumSpecifier) -> None:
        assert pyxx.logger is not None
        if self._publish[-1]:
            if enum_specifier.name is not None:
                attributes_parser = AttributeParser()
                enum_specifier.accept_attributes(attributes_parser)
                if attributes_parser.attributes.exported():
                    namespace = self.namespace
                    index = 0
                    partial_name = ''
                    if enum_specifier.name.is_absolute():
                        index = 1
                        partial_name = '::'
                        while self.namespace != self.namespace._parent:
                            self.namespace = self.namespace._parent
                    for name in enum_specifier.name.name_list[index:-1]:
                        sr = utils.StringRef()
                        name.accept(sr)
                        partial_name += sr.result + '::'
                        try:
                            self.namespace = self.namespace.get_child(sr.result)
                        except KeyError:
                            sr = utils.StringRef()
                            enum_specifier.name.accept(sr)
                            m0100(pyxx.logger, enum_specifier.name.position, sr.result, partial_name[:-2])
                            break
                    else:
                        sr = utils.StringRef()
                        enum_specifier.name.name_list[-1].accept(sr)
                        try:
                            self.namespace = self.namespace.get_child(sr.result)
                        except KeyError:
                            try:
                                exported, attributes = self.namespace.get_exported_object(sr.result)
                            except KeyError:
                                if len(enum_specifier.name.name_list) > 1:
                                    m0101(pyxx.logger, enum_specifier.name.position, sr.result, partial_name[:-2])
                                else:
                                    self.namespace = Enum(enum_specifier.position, attributes_parser.attributes,
                                                          sr.result, self.namespace)
                            else:
                                if exported:
                                    self.namespace = Enum(enum_specifier.position, attributes_parser.attributes,
                                                          sr.result, self.namespace)
                                else:
                                    self._publish.append(False)
                                    enum_specifier.accept_name(self)
                                    enum_specifier.accept_base_type(self)
                                    enum_specifier.accept_enumerators(self)
                                    self._publish.pop(-1)

                        else:
                            m0102(pyxx.logger, enum_specifier.position, sr.result)
                            m0012(pyxx.logger, self.namespace.position)
                        self.namespace = namespace
                else:
                    self._publish.append(False)
                    enum_specifier.accept_name(self)
                    enum_specifier.accept_base_type(self)
                    enum_specifier.accept_enumerators(self)
                    self._publish.pop(-1)
            else:
                self._publish.append(False)
                super().visit_enum_specifier(enum_specifier)
                self._publish.pop(-1)
        else:
            super().visit_enum_specifier(enum_specifier)

    def visit_member_declaration(self, access_specifier: ast.AccessSpecifier, declaration: ast.Declaration) -> None:
        if self._publish[-1]:
            access_specifier.accept(self)
            if self._access_specifier[-1] == 'public':
                declaration.accept(self)
            else:
                self._publish.append(False)
                super().visit_member_declaration(access_specifier, declaration)
                self._publish.pop(-1)
        else:
            super().visit_member_declaration(access_specifier, declaration)

    def visit_function_definition(self, function_definition: ast.FunctionDefinition) -> None:
        if self._publish[-1]:
            attributes_parser = AttributeParser()
            function_definition.accept_attributes(attributes_parser)
            if attributes_parser.attributes.exported():
                # look for class definitions in the decl-specifier-seq
                function_definition.accept_decl_specifier_seq(self)

                # also export declaration itself
                visitor = DeclarationVisitor(self._template_stack, attributes_parser.attributes, self.namespace)
                function_definition.accept_decl_specifier_seq(visitor)
                function_definition.accept_declarator(visitor)
                function_definition.accept_declarator(self)
                function_definition.accept_requires_clause(self)
                function_definition.accept_virt_specifier_seq(self)
                function_definition.accept_function_body(self)
            else:
                self._publish.append(False)
                function_definition.accept_decl_specifier_seq(self)
                function_definition.accept_declarator(self)
                function_definition.accept_requires_clause(self)
                function_definition.accept_virt_specifier_seq(self)
                function_definition.accept_function_body(self)
                self._publish.pop(-1)
        else:
            super().visit_function_definition(function_definition)

    def visit_access_specifier_default(self, access_specifier: ast.AccessSpecifierDefault) -> None:
        # leave default
        pass

    def visit_access_specifier_public(self, access_specifier: ast.AccessSpecifierPublic) -> None:
        if self._publish[-1]:
            self._access_specifier[-1] = 'public'

    def visit_access_specifier_protected(self, access_specifier: ast.AccessSpecifierProtected) -> None:
        if self._publish[-1]:
            self._access_specifier[-1] = 'protected'

    def visit_access_specifier_private(self, access_specifier: ast.AccessSpecifierPrivate) -> None:
        if self._publish[-1]:
            self._access_specifier[-1] = 'private'

    def visit_access_specifier_macro(self, access_specifier: ast.AccessSpecifierMacro) -> None:
        if self._publish[-1]:
            self._access_specifier[-1] = access_specifier.name

    def visit_elaborated_class_type_specifier(self,
                                              elaborated_class_type_specifier: ast.ElaboratedClassTypeSpecifier) -> None:
        if elaborated_class_type_specifier.name is not None:
            if len(elaborated_class_type_specifier.name.name_list) == 1:
                sr = utils.StringRef()
                elaborated_class_type_specifier.name.name_list[-1].accept(sr)
                attributes_parser = AttributeParser()
                elaborated_class_type_specifier.accept_attributes(attributes_parser)
                self.namespace.add_declared_object(sr.result,
                                                   self._publish[-1] and attributes_parser.attributes.exported(),
                                                   attributes_parser.attributes)
        else:
            super().visit_elaborated_class_type_specifier(elaborated_class_type_specifier)

    def visit_elaborated_enum_type_specifier(self,
                                             elaborated_enum_type_specifier: ast.ElaboratedEnumTypeSpecifier) -> None:
        if elaborated_enum_type_specifier.name is not None:
            if len(elaborated_enum_type_specifier.name.name_list) == 1:
                sr = utils.StringRef()
                elaborated_enum_type_specifier.name.name_list[-1].accept(sr)
                attributes_parser = AttributeParser()
                self.namespace.add_declared_object(sr.result,
                                                   self._publish[-1] and attributes_parser.attributes.exported(),
                                                   attributes_parser.attributes)
        else:
            super().visit_elaborated_enum_type_specifier(elaborated_enum_type_specifier)

    def visit_using_declaration(self, using_declaration: ast.UsingDeclaration) -> None:
        # TODO: can be used to bring a method into this struct/class.
        # nothing happens if the using member is not a method, or if no new overload is introduced.
        super().visit_using_declaration(using_declaration)

    def visit_template_declaration(self, template_declaration: ast.TemplateDeclaration) -> None:
        self._template_stack.append(Template())
        template_declaration.accept_declaration(self)
        if self._template_stack:
            assert pyxx.logger is not None
            m0300(pyxx.logger, template_declaration.position)
            # self._template_stack.clear()


def main() -> None:
    argument_context = pyxx.init_arguments()
    argument_context.add_argument(
        "-p", "--pch", dest="pch", help="Insert an include for precompiled header at the start of the file"
    )
    argument_context.add_argument("-m", "--module", dest="module", help="Module root")
    argument_context.add_argument("-r", "--root", dest="root", help="Namespace root")
    argument_context.add_argument(
        "in_relative",
        help="Include file relative to include node",
        metavar="INREL",
    )
    argument_context.add_argument(
        "out_relative",
        help="Output file relative to include node",
        metavar="OUTREL",
    )
    argument_context.add_argument(
        "out_cc",
        help="Output cc file",
        metavar="OUT_CC",
    )
    argument_context.add_argument(
        "out_typeid_cc",
        help="Output typeid.cc file",
        metavar="OUT_TYPEID_CC",
    )
    argument_context.add_argument(
        "out_hh",
        help="Output header file",
        metavar="OUT_HH",
    )
    argument_context.add_argument(
        "doc",
        help="Output doc file",
        metavar="OUT_DOC",
    )
    argument_context.add_argument(
        "namespace_exports",
        help="Output namespace export file",
        metavar="OUT_NAMESPACE_EXPORT",
    )

    arguments = argument_context.parse_args()
    results = pyxx.run(arguments)
    assert len(results) == 1
    file_name = re.sub('[^a-zA-Z0-9]', '_', arguments.in_relative)

    explorer = Explorer(file_name, arguments.module)
    results[0].accept(explorer)

    assert pyxx.logger is not None

    include_file = '<%s>' % arguments.out_relative
    if include_file not in results[0].included_files:
        m0200(pyxx.logger, (0, 0), include_file)

    if pyxx.logger.error_count:
        sys.exit(pyxx.logger.error_count)
    else:
        with open(arguments.out_cc, 'w') as out_cc:
            with open(arguments.out_typeid_cc, 'w') as out_typeid_cc:
                with open(arguments.out_hh, 'w') as out_hh:
                    out_cc.write('#include <%s>\n'
                                 '#include <motor/meta/object.meta.hh>\n'
                                 '#include <motor/meta/value.hh>\n'
                                 '' % arguments.out_relative)
                    out_typeid_cc.write('#include <%s>\n'
                                        '#include <motor/meta/object.meta.hh>\n'
                                        '#include <motor/meta/value.hh>\n'
                                        '' % arguments.out_relative)
                    out_hh.write('#ifndef MOTOR_COMPUTE\n'
                                 '#include <motor/meta/classinfo.hh>\n'
                                 '#include <%s>\n'
                                 '#include <motor/meta/builtins/numbers.hh>\n'
                                 '#include <motor/meta/builtins/strings.meta.hh>\n'
                                 '#include <motor/meta/builtins/value.meta.hh>\n'
                                 '\n' % (arguments.in_relative))
                    explorer.namespace.write_declarations([], out_cc, out_hh)
                    explorer.namespace.write_metaclasses([], out_typeid_cc, out_hh)
                    out_hh.write('#endif\n')

        with open(arguments.doc, 'w'):
            pass

        with open(arguments.namespace_exports, 'wb') as namespace_exports:
            pickle.dump((arguments.module, arguments.root, arguments.in_relative), namespace_exports)
            explorer.namespace.dump_exports([], namespace_exports)


if __name__ == '__main__':
    main()
