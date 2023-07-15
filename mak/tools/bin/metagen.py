import os
import sys
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0]))), 'libs'))
from pyxx import ast, utils

from typing import Dict, Optional, Tuple
import pickle


def get_meta_attributes(attribute_list):
    # default attributes
    attributes = {'export': True, 'alias': '', 'name': '', 'category': 'Object', 'type': ''}
    return attributes


class MetaObject(object):

    def __init__(self, parent: Optional["MetaObject"]) -> None:
        self._parent = parent if parent is not None else self
        self._children = {}  # type: Dict[str, MetaObject]
        self._namespace = (parent._namespace[0][:], parent._namespace[1][:]) if parent is not None else ([], [])
        self._objects = []

    def file_name(self) -> str:
        return self._parent.file_name()

    def dump_exports(self, namespace, out_classes, out_namespace):
        for name, child in self._children.items():
            namespace.append(name)
            child.dump_exports(namespace, out_classes, out_namespace)
            namespace.pop(-1)

    def write_declarations(self, namespace, out):
        for name, child in self._children.items():
            namespace.append(name)
            child.write_declarations(namespace, out)
            namespace.pop(-1)

    def write_metaclasses(self, namespace, out):
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
        raise NotImplemented


class RootNamespace(MetaObject):
    def __init__(self, file_name: str, module_name: str) -> None:
        super().__init__(None)
        self._file_name = file_name
        self._cpp_name = 'motor_%s_Namespace' % module_name

    def file_name(self) -> str:
        return self._file_name

    def name(self) -> str:
        return '::Motor::' + self._cpp_name + '()'

    def write_declarations(self, namespace, out):
        out.write('namespace Motor { raw<Meta::Class> %s(); }\n' % self._cpp_name)
        super().write_declarations(namespace, out)


class Namespace(MetaObject):

    def __init__(self, name: str, parent: MetaObject) -> None:
        super().__init__(parent)
        self._name = name
        self._cpp_name = parent._cpp_name + '_' + name
        parent._children[name] = self
        self._namespace[0].append(name)

    def dump_exports(self, namespace, out_classes, out_namespace):
        pickle.dump(namespace, out_namespace)
        super().dump_exports(namespace, out_classes, out_namespace)

    def write_declarations(self, namespace, out):
        out.write('namespace Motor { raw<Meta::Class> %s(); }\n' % self._cpp_name)
        super().write_declarations(namespace, out)

    def name(self) -> str:
        return '::Motor::' + self._cpp_name + '()'


class Class(MetaObject):

    def __init__(self, name: str, is_value_type: bool, superclass: Optional[str], parent: MetaObject) -> None:
        super().__init__(parent)
        self._name = name
        parent._children[name] = self
        self._superclass = superclass if superclass is not None else 'void'
        self._fields = []
        self._methods = []
        self._namespace[1].append(name)
        self._is_value_type = is_value_type

    def name(self):
        return 'motor_class<::%s>()' % '::'.join(self._namespace[0] + self._namespace[1])

    def object_name(self):
        return '%s_Meta::name()' % self._name, 'static_cast<raw<const ::Motor::Meta::Class>>(%s_Meta::klass())' % self._name

    def dump_exports(self, namespace, out_classes, out_namespace):
        pickle.dump(self._namespace, out_classes)
        super().dump_exports(namespace, out_classes, out_namespace)

    def write_metaclasses(self, namespace, out):
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

    def __init__(self, name: str, parent: MetaObject) -> None:
        super().__init__(name, True, None, parent)


class BaseClauseVisitor(ast.Visitor):
    def __init__(self, is_default_public: bool) -> None:
        self.base_clause = None  # tyoe: Optional[str]
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


class Explorer(ast.Visitor):

    def __init__(self, file_name: str, module_name: str) -> None:
        self._namespace = RootNamespace(file_name, module_name)
        self._access_specifier = []

    def visit_translation_unit(self, translation_unit: ast.TranslationUnit) -> None:
        translation_unit.accept_children(self)

    def visit_namespace_declaration(self, namespace_declaration: ast.NamespaceDeclaration) -> None:
        if namespace_declaration._namespace_name is not None:
            namespace = self._namespace
            for _, name in namespace_declaration._nested_name:
                try:
                    self._namespace = self._namespace._children[name]
                except KeyError:
                    self._namespace = Namespace(name, self._namespace)
            try:
                self._namespace = self._namespace._children[namespace_declaration._namespace_name]
            except KeyError:
                self._namespace = Namespace(namespace_declaration._namespace_name, self._namespace)
            namespace_declaration.accept_children(self)
            self._namespace = namespace

    def visit_ambiguous_declaration(self, ambiguous_declaration):
        # type: (ast.AmbiguousDeclaration) -> None
        ambiguous_declaration.accept_first(self)

    def visit_simple_declaration(self, simple_declaration):
        # look for class definitions in the decl-specifier-seq
        simple_declaration.accept_decl_specifier_seq(self)

        # also export declaration itself, if necessary
        # TODO

    def visit_decl_specifier_seq(self, decl_specifier_seq):
        # type: (ast.DeclSpecifierSeq) -> None
        # look for class definitions in the type specifiers of the decl-specifier-seq
        decl_specifier_seq.accept_type_specifier_seq(self)

    def visit_type_specifier_seq(self, type_specifier_seq):
        # type: (ast.TypeSpecifierSeq) -> None
        # look for class definitions in the type specifiers
        type_specifier_seq.accept_types(self)

    def visit_class_specifier(self, class_specifier):
        # type: (ast.ClassSpecifier) -> None
        if class_specifier._name is not None:
            base_clause_visitor = BaseClauseVisitor(class_specifier._class_type != 'class')
            class_specifier.accept_base_clause(base_clause_visitor)
            namespace = self._namespace
            for name in class_specifier._name._name_list[:-1]:
                sr = utils.StringRef()
                name.accept(sr)
                try:
                    self._namespace = self._namespace._children[sr.result]
                except KeyError:
                    self._namespace = Namespace(sr.result, self._namespace)
            sr = utils.StringRef()
            class_specifier._name._name_list[-1].accept(sr)
            try:
                self._namespace = self._namespace._children[sr.result]
            except KeyError:
                self._namespace = Class(sr.result, class_specifier._class_type != 'class',
                                        base_clause_visitor.base_clause, self._namespace)
            self._access_specifier.append(
                class_specifier._class_type in ('struct', 'union') and 'published' or 'private')
            class_specifier.accept_members(self)
            self._access_specifier.pop(-1)
            self._namespace = namespace

    def visit_enum_specifier(self, enum_specifier):
        # type: (ast.EnumSpecifier) -> None
        if enum_specifier._name is not None:
            namespace = self._namespace
            for name in enum_specifier._name._name_list[:-1]:
                sr = utils.StringRef()
                name.accept(sr)
                try:
                    self._namespace = self._namespace._children[sr.result]
                except KeyError:
                    self._namespace = Namespace(sr.result, self._namespace)
            sr = utils.StringRef()
            enum_specifier._name._name_list[-1].accept(sr)
            try:
                self._namespace = self._namespace._children[sr.result]
            except KeyError:
                self._namespace = Enum(sr.result, self._namespace)
            self._namespace = namespace

    def visit_member_declaration(self, access_specifier, declaration):
        # type: (ast.AccessSpecifier, ast.Declaration) -> None
        access_specifier.accept(self)
        if self._access_specifier[-1] == 'published':
            declaration.accept(self)

    def visit_function_definition(self, function_definition):
        # type: (ast.FunctionDefinition) -> None
        # look for class definitions in the decl-specifier-seq
        function_definition.accept_decl_specifier_seq(self)
        # also export declaration itself, if necessary
        # TODO

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


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0]))), 'libs'))
    import pyxx

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

    with open(arguments.out, 'w') as out:
        out.write('#include <motor/meta/typeinfo.hh>\n'
                  '#include "%s"\n'
                  '#include <motor/meta/object.meta.hh>\n'
                  '#include <motor/meta/value.hh>\n'
                  '#include <motor/meta/interfacetable.hh>\n'
                  '%s\n\n' % (arguments.in_relative, '\n'.join('#include %s' % i for i in results[0]._included_files)))
        explorer._namespace.write_declarations([], out)
        explorer._namespace.write_metaclasses([], out)

    with open(arguments.doc, 'w') as doc:
        pass

    with open(arguments.class_exports, 'wb') as class_exports:
        with open(arguments.namespace_exports, 'wb') as namespace_exports:
            pickle.dump((arguments.module, arguments.root, arguments.in_relative), class_exports)
            pickle.dump((arguments.module, arguments.root, arguments.in_relative), namespace_exports)
            explorer._namespace.dump_exports([], class_exports, namespace_exports)
