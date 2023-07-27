import io
import os
import sys
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0]))), 'libs'))
import pyxx
import glrp
from pyxx import ast, utils, messages

from typing import Dict, Optional, Tuple, Any, List
import pickle


@messages.error
def M0000(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """unknown attribute motor::{attribute}"""
    return locals()


@messages.error
def M0001(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """unknown meta attribute {attribute}"""
    return locals()


@messages.error
def M0002(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """trailing tokens after attribute {attribute}"""
    return locals()


@messages.error
def M0003(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """invalid value for attribute {attribute}"""
    return locals()


@messages.warning('ignored-attribute', True)
def M0004(logger: messages.Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """motor attribute ignored"""
    return locals()


@messages.warning('ignored-attribute', True)
def M0005(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """motor attribute {attribute} ignored due to export directive"""
    return locals()


@messages.diagnostic
def M0006(logger: messages.Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """export directive here"""
    return locals()


@messages.warning('ignored-attribute', True)
def M0007(logger: messages.Logger, position: Tuple[int, int], attribute: str, object_type: str) -> Dict[str, Any]:
    """motor attribute {attribute} ignored on object of type {object_type}"""
    return locals()


@messages.error
def M0010(logger: messages.Logger, position: Tuple[int, int], export: str) -> Dict[str, Any]:
    """invalid value {export} for export attribute"""
    return locals()


@messages.warning('multiple-attribute', True)
def M0011(logger: messages.Logger, position: Tuple[int, int], attribute: str) -> Dict[str, Any]:
    """multiple definitions for attribute {attribute}"""
    return locals()


@messages.diagnostic
def M0012(logger: messages.Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """previous definition here"""
    return locals()


class Attributes(object):
    def __init__(self) -> None:
        self._export = None  # type: Optional[Tuple[Tuple[int, int], bool]]
        self._documentation = []  # type: List[Tuple[Tuple[int, int], str]]
        self._interfaces = []  # type: List[Tuple[Tuple[int, int], str]]
        self._name = None  # type: Optional[Tuple[Tuple[int, int], str]]
        self._alias = []  # type: List[Tuple[Tuple[int, int], str]]
        self._tags = []  # type: List[Tuple[Tuple[int, int], List[glrp.Token]]]

    def export(self) -> bool:
        return self._export is None or self._export[1]


class MetaObject(object):

    def __init__(self, attributes: Attributes, parent: Optional["MetaObject"]) -> None:
        self._attributes = attributes
        self._parent = parent if parent is not None else self
        self._children = {}  # type: Dict[str, MetaObject]
        self._namespace = (parent._namespace[0][:], parent._namespace[1][:]) if parent is not None else (
            [], [])  # type: Tuple[List[str], List[str]]
        self._objects = []  # type: List[MetaObject]

    def file_name(self) -> str:
        return self._parent.file_name()

    def dump_exports(self, namespace: List[str], out_classes: io.BufferedWriter,
                     out_namespace: io.BufferedWriter) -> None:
        for name, child in self._children.items():
            namespace.append(name)
            child.dump_exports(namespace, out_classes, out_namespace)
            namespace.pop(-1)

    def write_declarations(self, namespace: List[str], out: io.TextIOWrapper) -> None:
        for name, child in self._children.items():
            namespace.append(name)
            child.write_declarations(namespace, out)
            namespace.pop(-1)

    def write_metaclasses(self, namespace: List[str], out: io.TextIOWrapper) -> None:
        object_names = []
        for name, child in self._children.items():
            namespace.append(name)
            child.write_metaclasses(namespace, out)
            o = child.object_name()
            if o is not None:
                object_names.append(o)
            namespace.pop(-1)
        if object_names:
            file_name = self.file_name()
            owner_name = self._parent.name()
            if namespace:
                out.write('\nnamespace %s\n'
                          '{\n'
                          '\n' % (' { namespace '.join(namespace)))
            out.write('static ::Motor::Meta::Object s_%s_objects[%d] = {\n' % (file_name, len(object_names)))
            for i, (object_name, object_value) in enumerate(object_names):
                if i < len(object_names) - 1:
                    next = '{&s_%s_objects[%d]}' % (file_name, i + 1)
                    comma = ','
                else:
                    next = '%s->objects' % owner_name
                    comma = ''
                out.write('    {\n'
                          '        %s,\n'
                          '        {nullptr},\n'
                          '        %s,\n'
                          '        ::Motor::Meta::Value(%s)\n'
                          '    }%s\n' % (next, object_name, object_value, comma))
            out.write('};\n'
                      'MOTOR_EXPORT const ::Motor::Meta::Object* s_%s_registry = %s->objects.set(s_%s_objects);\n'
                      '\n' % (file_name, owner_name, file_name))
            if namespace:
                out.write('%s\n' % ('}' * len(namespace)))

    def object_name(self) -> Optional[Tuple[str, str]]:
        return None

    def name(self) -> str:
        raise NotImplementedError

    def cpp_name(self) -> str:
        raise NotImplementedError


class RootNamespace(MetaObject):
    def __init__(self, file_name: str, module_name: str):
        super().__init__(Attributes(), None)
        self._file_name = file_name
        self._cpp_name = 'motor_%s_Namespace' % module_name

    def cpp_name(self) -> str:
        return self._cpp_name

    def file_name(self) -> str:
        return self._file_name

    def name(self) -> str:
        return '::Motor::' + self._cpp_name + '()'

    def write_declarations(self, namespace: List[str], out: io.TextIOWrapper):
        out.write('namespace Motor { raw<Meta::Class> %s(); }\n' % self._cpp_name)
        super().write_declarations(namespace, out)


class Namespace(MetaObject):

    def __init__(self, attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(attributes, parent)
        self._name = name
        self._cpp_name = parent.cpp_name() + '_' + name
        parent._children[name] = self
        self._namespace[0].append(name)
        assert pyxx.logger is not None
        for position, interface in attributes._interfaces:
            M0007(pyxx.logger, position, 'interface', 'namespace')

    def cpp_name(self) -> str:
        return self._cpp_name

    def dump_exports(self, namespace: List[str], out_classes: io.BufferedWriter, out_namespace: io.BufferedWriter):
        pickle.dump(namespace, out_namespace)
        super().dump_exports(namespace, out_classes, out_namespace)

    def write_declarations(self, namespace: List[str], out: io.TextIOWrapper):
        out.write('namespace Motor { raw<Meta::Class> %s(); }\n' % self._cpp_name)
        super().write_declarations(namespace, out)

    def name(self) -> str:
        return '::Motor::' + self._cpp_name + '()'


class Class(MetaObject):

    def __init__(self, attributes: Attributes, name: str, is_value_type: bool, superclass: Optional[str],
                 parent: MetaObject):
        super().__init__(attributes, parent)
        self._name = name
        parent._children[name] = self
        self._superclass = superclass if superclass is not None else 'void'
        self._namespace[1].append(name)
        self._is_value_type = is_value_type

    def name(self) -> str:
        return 'motor_class<::%s>()' % '::'.join(self._namespace[0] + self._namespace[1])

    def object_name(self) -> Tuple[str, str]:
        return '%s_Meta::name()' % self._name, 'static_cast<raw<const ::Motor::Meta::Class>>(%s_Meta::klass())' % self._name

    def dump_exports(self, namespace: List[str], out_classes: io.BufferedWriter, out_namespace: io.BufferedWriter):
        pickle.dump(self._namespace, out_classes)
        super().dump_exports(namespace, out_classes, out_namespace)

    def write_metaclasses(self, namespace: List[str], out: io.TextIOWrapper):
        full_name = '::'.join(namespace)
        owner = self._parent.name()

        object_names = []
        for name, child in self._children.items():
            namespace.append(name)
            child.write_metaclasses(namespace, out)
            o = child.object_name()
            if o is not None:
                object_names.append(o)
            namespace.pop(-1)

        if self._namespace[0]:
            out.write('\nnamespace %s { namespace %s_Meta\n{\n' % (
                ' { namespace '.join(self._namespace[0]), '_Meta { namespace '.join(self._namespace[1])))
        else:
            out.write('\nnamespace %s_Meta\n{\n' % ('_Meta { namespace '.join(self._namespace[1])))

        objects = '::Motor::Meta::ClassID<%s>::klass()->objects' % self._superclass
        if object_names:
            out.write('static ::Motor::Meta::Object s_objects[%d] = {\n' % (len(object_names)))
            for i, (object_name, object_value) in enumerate(object_names):
                if i < len(object_names) - 1:
                    next = '{&s_objects[%d]}' % (i + 1)
                    comma = ','
                else:
                    next = objects
                    comma = ''
                out.write('    {\n'
                          '        %s,\n'
                          '        {nullptr},\n'
                          '        %s,\n'
                          '        ::Motor::Meta::Value(%s)\n'
                          '    }%s\n' % (next, object_name, object_value, comma))
            out.write('};\n')
            objects = '{s_objects}'
        if self._superclass != 'void':
            offset = 'static_cast<i32>(reinterpret_cast<char*>(static_cast<%s*>(reinterpret_cast<%s*>(1)))-reinterpret_cast<char*>(1))' % (
                self._superclass, full_name)
        else:
            offset = '0'
        parent = '::Motor::Meta::ClassID<%s>::klass()' % self._superclass
        properties = '::Motor::Meta::ClassID<%s>::klass()->properties' % self._superclass
        methods = '::Motor::Meta::ClassID<%s>::klass()->methods' % self._superclass
        tags = '::Motor::Meta::ClassID<%s>::klass()->tags' % self._superclass
        interfaces = '::Motor::Meta::ClassID<%s>::klass()->interfaces' % self._superclass

        if self._is_value_type:
            copyconstructor = '&copyconstructor'
            destructor = '&destructor'
        else:
            copyconstructor = 'nullptr'
            destructor = 'nullptr'
        if self._is_value_type:
            out.write('static void copyconstructor(const void* source, void* destination)\n'
                      '{\n'
                      '    new(destination) %s(*(const %s*)source);\n'
                      '}\n'
                      'static void destructor(void* value)\n'
                      '{\n'
                      '    typedef %s T;\n'
                      '    ((T*)value)->~T();\n'
                      '}\n' % (full_name, full_name, full_name))

        out.write('::Motor::istring name()\n'
                  '{\n'
                  '    static const ::Motor::istring s_name("%s");\n'
                  '    return s_name;\n'
                  '}\n' % self._name)
        out.write('raw<::Motor::Meta::Class> klass()\n'
                  '{\n'
                  '    static ::Motor::Meta::Class s_klass = {\n'
                  '        name(),\n'
                  '        sizeof(%s),\n'
                  '        %s,\n'
                  '        %s,\n'
                  '        %s,\n'
                  '        %s,\n'
                  '        %s,\n'
                  '        %s,\n'
                  '        {nullptr},\n'
                  '        %s,\n'
                  '        %s,\n'
                  '        %s\n'
                  '    };\n'
                  '    return {&s_klass};\n'
                  '}\n' % (full_name, parent, offset, objects, tags, properties, methods, interfaces, copyconstructor,
                           destructor))
        out.write('%s\n\n' % ('}' * (len(namespace))))


class Enum(Class):
    def __init__(self, attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(attributes, name, True, None, parent)


class Method(MetaObject):
    def __init__(self, attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(attributes, parent)
        self._name = name


class Variable(MetaObject):
    def __init__(self, attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(attributes, parent)
        self._name = name


class TypeDef(MetaObject):
    def __init__(self, attributes: Attributes, name: str, parent: MetaObject):
        super().__init__(attributes, parent)
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
        self._attributes = Attributes()

    def parse_meta_attributes(self, tokens: List[glrp.Token]) -> None:
        assert pyxx.logger is not None
        tokens = tokens[:]

        def skip(tokens):
            depth = 0
            while tokens:
                token = tokens.pop(0).text()
                if token == ',' and depth == 0:
                    break
                elif token in ('(', '[', '{'):
                    depth += 1
                elif token in (')', ']', '}'):
                    depth -= 1

        while tokens:
            attribute_token = tokens.pop(0)
            attribute = attribute_token.text()
            if attribute == 'noexport':
                if self._attributes._export is not None:
                    if (M0011(pyxx.logger, attribute_token.position, 'export')):
                        M0012(pyxx.logger, self._attributes._export[0])
                self._attributes._export = (attribute_token.position, False)
            elif attribute == 'export':
                if self._attributes._export is not None:
                    if (M0011(pyxx.logger, attribute_token.position, 'export')):
                        M0012(pyxx.logger, self._attributes._export[0])
                if len(tokens) > 1 and tokens[0].text() == '=':
                    tokens.pop(0)
                    export_token = tokens.pop(0)
                    export = export_token.text()
                    if export in ('yes', 'true', '1'):
                        self._attributes._export = (attribute_token.position, True)
                    elif export in ('no', 'false', '0'):
                        self._attributes._export = (attribute_token.position, False)
                    else:
                        M0010(pyxx.logger, export_token.position, export)
                else:
                    self._attributes._export = (attribute_token.position, True)
            elif attribute == 'name':
                if self._attributes._name is not None:
                    if (M0011(pyxx.logger, attribute_token.position, attribute)):
                        M0012(pyxx.logger, self._attributes._name[0])
                elif len(tokens) < 2 or tokens[0].text() != '=':
                    M0003(pyxx.logger, attribute_token.position, attribute)
                    skip(tokens)
                else:
                    tokens.pop(0)
                    self._attributes._name = (attribute_token.position, tokens.pop(0).text())
            elif attribute == 'alias':
                if len(tokens) < 2 or tokens[0].text() != '=':
                    M0003(pyxx.logger, attribute_token.position, attribute)
                    skip(tokens)
                else:
                    tokens.pop(0)
                    self._attributes._alias.append((attribute_token.position, tokens.pop(0).text()))
            elif attribute == 'tag':
                if len(tokens) < 2 or tokens[0].text() != '=':
                    M0003(pyxx.logger, attribute_token.position, attribute)
                    skip(tokens)
                else:
                    tokens.pop(0)
                    tag = []  # type: List[glrp.Token]
                    self._attributes._tags.append((attribute_token.position, tag))
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
                    M0003(pyxx.logger, attribute_token.position, attribute)
                    skip(tokens)
                else:
                    tokens.pop(0)
                    self._attributes._interfaces.append((attribute_token.position, tokens.pop(0).text()))

            else:
                M0001(pyxx.logger, attribute_token.position, attribute)
                skip(tokens)
            if tokens:
                if tokens[0].text() == ',':
                    tokens.pop(0)
                    continue
                else:
                    M0002(pyxx.logger, tokens[0].position, attribute)
                    skip(tokens)
        if not self._attributes.export():
            assert self._attributes._export is not None
            show_position = False
            for position, _ in self._attributes._documentation:
                show_position |= M0005(pyxx.logger, position, 'documentation')
            for position, _ in self._attributes._interfaces:
                show_position |= M0005(pyxx.logger, position, 'interface')
            if self._attributes._name is not None:
                show_position |= M0005(pyxx.logger, self._attributes._name[0], 'name')
            for position, _ in self._attributes._alias:
                show_position |= M0005(pyxx.logger, position, 'alias')
            for position, _ in self._attributes._tags:
                show_position |= M0005(pyxx.logger, position, 'tag')
            if show_position:
                M0006(pyxx.logger, self._attributes._export[0])

    def visit_attribute_named_list(self, attribute_named_list: ast.AttributeNamedList) -> None:
        attribute_named_list.accept_attributes(self)

    def visit_attribute_named(self, using_namespace: Optional[str], attribute_named: ast.AttributeNamed) -> None:
        if using_namespace != 'motor' and attribute_named._namespace != 'motor':
            return
        if attribute_named._attribute != 'meta':
            assert pyxx.logger is not None
            M0000(pyxx.logger, attribute_named.position, attribute_named._attribute)
            return
        if attribute_named._value is None:
            return
        self.parse_meta_attributes(attribute_named._value)

    def visit_attribute_macro(self, attribute_macro: ast.AttributeMacro) -> None:
        if attribute_macro._attribute != 'motor_meta':
            return
        if attribute_macro._values:
            if attribute_macro._values[0].text() == '(':
                self.parse_meta_attributes(attribute_macro._values[1:-1])
            else:
                self.parse_meta_attributes(attribute_macro._values)


class DeclarationVisitor(ast.Visitor):
    def __init__(self, attributes: Attributes, namespace: MetaObject):
        super().__init__()
        self._attributes = attributes
        self._namespace = namespace

    def visit_decl_specifier_seq(self, decl_specifier_seq: ast.DeclSpecifierSeq) -> None:
        decl_specifier_seq.accept_decl_specifiers(self)

    def visit_declaration_specifier(self, declaration_specifier: ast.DeclarationSpecifier) -> None:
        pass

    def visit_storage_class_specifier(self, storage_class_specifier: ast.StorageClassSpecifier) -> None:
        # print(storage_class_specifier._decl_specifier)
        pass

    def visit_init_declarator_list(self, init_declarator_list: ast.InitDeclaratorList) -> None:
        for init_declarator in init_declarator_list._init_declarators:
            init_declarator.accept(self)

    def visit_init_declarator(self, init_declarator: ast.InitDeclarator) -> None:
        init_declarator.accept_declarator(self)

    def visit_declarator_list(self, declarator_list: ast.DeclaratorList) -> None:
        if declarator_list.is_method():
            pass


class Explorer(utils.RecursiveVisitor):

    def __init__(self, file_name: str, module_name: str):
        self._namespace = RootNamespace(file_name, module_name)  # type: MetaObject
        self._access_specifier = []  # type: List[str]
        self._publish = [True]

    def visit_attribute_named(self, using_namespace: Optional[str], attribute_named: ast.AttributeNamed) -> None:
        assert pyxx.logger is not None
        if using_namespace != 'motor' and attribute_named._namespace != 'motor':
            return
        if attribute_named._attribute != 'meta':
            M0000(pyxx.logger, attribute_named.position, attribute_named._attribute)
            return
        if attribute_named._value is None:
            return
        M0004(pyxx.logger, attribute_named.position)

    def visit_attribute_macro(self, attribute_macro: ast.AttributeMacro) -> None:
        assert pyxx.logger is not None
        if attribute_macro._attribute != 'motor_meta':
            return
        M0004(pyxx.logger, attribute_macro.position)

    def visit_template_declaration(self, template_declaration: ast.TemplateDeclaration) -> None:
        self._publish.append(False)
        super().visit_template_declaration(template_declaration)
        self._publish.pop(-1)

    def visit_compound_statement(self, compound_statement: ast.CompoundStatement) -> None:
        self._publish.append(False)
        super().visit_compound_statement(compound_statement)
        self._publish.pop(-1)

    def visit_namespace_declaration(self, namespace_declaration: ast.NamespaceDeclaration) -> None:
        if self._publish[-1]:
            if namespace_declaration._namespace_name is not None:
                attribute_parser = AttributeParser()
                namespace_declaration.accept_attributes(attribute_parser)
                if attribute_parser._attributes.export():
                    namespace = self._namespace
                    for _, name in namespace_declaration._nested_name:
                        try:
                            self._namespace = self._namespace._children[name]
                        except KeyError:
                            self._namespace = Namespace(Attributes(), name, self._namespace)
                    try:
                        self._namespace = self._namespace._children[namespace_declaration._namespace_name]
                    except KeyError:
                        self._namespace = Namespace(attribute_parser._attributes, namespace_declaration._namespace_name,
                                                    self._namespace)
                    namespace_declaration.accept_children(self)
                    self._namespace = namespace
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

    def visit_simple_declaration(self, simple_declaration: ast.SimpleDeclaration):
        if self._publish[-1]:
            attribute_parser = AttributeParser()
            simple_declaration.accept_attributes(attribute_parser)
            if attribute_parser._attributes.export():
                # look for class definitions in the decl-specifier-seq
                simple_declaration.accept_decl_specifier_seq(self)

                # also export declaration itself
                visitor = DeclarationVisitor(attribute_parser._attributes, self._namespace)
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
        if self._publish[-1]:
            if class_specifier._name is not None:
                attributes_parser = AttributeParser()
                class_specifier.accept_attributes(attributes_parser)
                if attributes_parser._attributes.export():
                    base_clause_visitor = BaseClauseVisitor(class_specifier._class_type != 'class')
                    class_specifier.accept_base_clause(base_clause_visitor)
                    namespace = self._namespace
                    for name in class_specifier._name._name_list[:-1]:
                        sr = utils.StringRef()
                        name.accept(sr)
                        try:
                            self._namespace = self._namespace._children[sr.result]
                        except KeyError:
                            self._namespace = Namespace(attributes_parser._attributes, sr.result, self._namespace)
                    sr = utils.StringRef()
                    class_specifier._name._name_list[-1].accept(sr)
                    try:
                        self._namespace = self._namespace._children[sr.result]
                    except KeyError:
                        self._namespace = Class(attributes_parser._attributes, sr.result,
                                                class_specifier._class_type != 'class',
                                                base_clause_visitor.base_clause, self._namespace)
                    self._access_specifier.append(
                        class_specifier._class_type in ('struct', 'union') and 'public' or 'private')
                    class_specifier.accept_members(self)
                    self._access_specifier.pop(-1)
                    self._namespace = namespace
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
        if self._publish[-1]:
            if enum_specifier._name is not None:
                attributes_parser = AttributeParser()
                enum_specifier.accept_attributes(attributes_parser)
                if attributes_parser._attributes.export():
                    namespace = self._namespace
                    for name in enum_specifier._name._name_list[:-1]:
                        sr = utils.StringRef()
                        name.accept(sr)
                        try:
                            self._namespace = self._namespace._children[sr.result]
                        except KeyError:
                            self._namespace = Namespace(attributes_parser._attributes, sr.result, self._namespace)
                    sr = utils.StringRef()
                    enum_specifier._name._name_list[-1].accept(sr)
                    try:
                        self._namespace = self._namespace._children[sr.result]
                    except KeyError:
                        self._namespace = Enum(attributes_parser._attributes, sr.result, self._namespace)
                    self._namespace = namespace
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
            if attributes_parser._attributes.export():
                # look for class definitions in the decl-specifier-seq
                function_definition.accept_decl_specifier_seq(self)

                # also export declaration itself
                visitor = DeclarationVisitor(attributes_parser._attributes, self._namespace)
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
        self._access_specifier[-1] = 'public'

    def visit_access_specifier_protected(self, access_specifier: ast.AccessSpecifierProtected) -> None:
        self._access_specifier[-1] = 'protected'

    def visit_access_specifier_private(self, access_specifier: ast.AccessSpecifierPrivate) -> None:
        self._access_specifier[-1] = 'private'

    def visit_access_specifier_macro(self, access_specifier: ast.AccessSpecifierMacro) -> None:
        self._access_specifier[-1] = access_specifier._name


def main() -> None:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0]))), 'libs'))

    argument_context = pyxx.init_arguments()
    argument_context.add_argument(
        "-p", "--pch", dest="pch", help="Insert an include for precompiled header at the start of the file"
    )
    argument_context.add_argument("-m", "--module", dest="module", help="Module root")
    argument_context.add_argument("-r", "--root", dest="root", help="Namespace root")
    argument_context.add_argument(
        "in_relative",
        help="Input file relative to srcnode",
        metavar="INREL",
    )
    argument_context.add_argument(
        "out",
        help="Output cc file",
        metavar="OUT",
    )
    argument_context.add_argument(
        "doc",
        help="Output doc file",
        metavar="DOC",
    )
    argument_context.add_argument(
        "class_exports",
        help="Output class export file",
        metavar="CLS_EXPORT",
    )
    argument_context.add_argument(
        "namespace_exports",
        help="Output namespace export file",
        metavar="NAMESPACE_EXPORT",
    )

    arguments = argument_context.parse_args()
    results = pyxx.run(arguments)
    assert len(results) == 1
    file_name = re.sub('[^a-zA-Z0-9]', '_', arguments.in_relative)

    explorer = Explorer(file_name, arguments.module)
    results[0].accept(explorer)

    assert pyxx.logger is not None
    if pyxx.logger._error_count:
        sys.exit(pyxx.logger._error_count)
    else:
        with open(arguments.out, 'w') as out:
            out.write('#include <motor/meta/typeinfo.hh>\n'
                      '#include "%s"\n'
                      '#include <motor/meta/object.meta.hh>\n'
                      '#include <motor/meta/value.hh>\n'
                      '#include <motor/meta/interfacetable.hh>\n'
                      '%s\n\n' % (
                          arguments.in_relative, '\n'.join('#include %s' % i for i in results[0]._included_files)))
            explorer._namespace.write_declarations([], out)
            explorer._namespace.write_metaclasses([], out)

        with open(arguments.doc, 'w') as doc:
            pass

        with open(arguments.class_exports, 'wb') as class_exports:
            with open(arguments.namespace_exports, 'wb') as namespace_exports:
                pickle.dump((arguments.module, arguments.root, arguments.in_relative), class_exports)
                pickle.dump((arguments.module, arguments.root, arguments.in_relative), namespace_exports)
                explorer._namespace.dump_exports([], class_exports, namespace_exports)


if __name__ == '__main__':
    main()
