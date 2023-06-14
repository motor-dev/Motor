import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0]))), 'libs'))
from pyxx import ast, utils

from typing import Dict, Optional
import pickle


def get_meta_attributes(attribute_list):
    # default attributes
    attributes = {'export': True, 'alias': '', 'name': '', 'category': 'Object', 'type': ''}
    return attributes


class MetaObject(object):

    def __init__(self, parent: Optional["MetaObject"]) -> None:
        self._parent = parent if parent is not None else self
        self._children = {}  # type: Dict[str, MetaObject]
        self._namespace = parent._namespace[:] if parent is not None else []

    def dump_exports(self, namespace, out):
        for name, child in self._children.items():
            namespace.append(name)
            child.dump_exports(namespace, out)
            namespace.pop(-1)

    def write_declarations(self, namespace, out):
        for name, child in self._children.items():
            namespace.append(name)
            child.write_declarations(namespace, out)
            namespace.pop(-1)

    def write_metaclasses(self, namespace, out):
        for name, child in self._children.items():
            namespace.append(name)
            child.write_metaclasses(namespace, out)
            namespace.pop(-1)

    def name(self) -> str:
        raise NotImplemented


class RootNamespace(MetaObject):
    def __init__(self, module_name: str) -> None:
        super().__init__(None)
        self._cpp_name = 'motor_%s_Namespace' % module_name

    def name(self) -> str:
        return '::Motor::' + self._cpp_name + '()'


class Namespace(MetaObject):

    def __init__(self, name: str, parent: MetaObject) -> None:
        super().__init__(parent)
        self._name = name
        self._cpp_name = parent._cpp_name + '_' + name
        parent._children[name] = self
        self._namespace.append(name)

    def dump_exports(self, namespace, out):
        pickle.dump(('ns', namespace), out)
        super().dump_exports(namespace, out)

    def write_declarations(self, namespace, out):
        out.write('namespace Motor { MOTOR_EXPORT raw<Meta::Class> %s(); }\n' % self._cpp_name)
        super().write_declarations(namespace, out)

    def name(self) -> str:
        return '::Motor::' + self._cpp_name + '()'


class Class(MetaObject):

    def __init__(self, name: str, superclass: Optional[str], parent: MetaObject) -> None:
        super().__init__(parent)
        self._name = name
        parent._children[name] = self
        self._superclass = superclass
        self._fields = []
        self._methods = []
        self._namespace.append(name)

    def dump_exports(self, namespace, out):
        pickle.dump(('class', namespace), out)
        super().dump_exports(namespace, out)

    def write_metaclasses(self, namespace, out):
        full_name = '::'.join(namespace)

        if self._superclass is not None:
            offset = 'static_cast<i32>(reinterpret_cast<char*>(static_cast<%s*>(reinterpret_cast<%s*>(1)))-reinterpret_cast<char*>(1))' % (
                self._superclass, full_name)
            parent = '::Motor::Meta::ClassID<%s>::klass()' % self._superclass
            operators = '::Motor::Meta::ClassID<%s>::klass()->operators' % self._superclass
        else:
            offset = '0'
            parent = '::Motor::Meta::ClassID<void>::klass()'
            operators = '::Motor::Meta::OperatorTable::s_emptyTable'

        out.write('\nnamespace %s_Meta\n{\n' % (' { namespace '.join(namespace)))
        out.write('::Motor::istring name()\n'
                  '{\n'
                  '    static const ::Motor::istring s_name("%s");\n'
                  '    return s_name;\n'
                  '}\n' % namespace[-1])
        out.write('::Motor::Meta::Class s_klass = {\n'
                  '    name(),\n'
                  '    sizeof(%s),\n'
                  '    %s,\n'
                  '    0,\n'
                  '    %s,\n'
                  '    %s,\n'
                  '    {nullptr},\n'
                  '    {nullptr},\n'
                  '    {0, nullptr},\n'
                  '    {0, nullptr},\n'
                  '    {nullptr},\n'
                  '    %s,\n'
                  '    nullptr,\n'
                  '    nullptr\n'
                  '};\n' % (full_name, offset, self._parent.name(), parent, operators))
        out.write('%s\n\n' % ('}' * (len(namespace))))


class Enum(Class):

    def __init__(self, name: str, parent: MetaObject) -> None:
        super().__init__(name, None, parent)


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

    def __init__(self, module_name: str) -> None:
        self._namespace = RootNamespace(module_name)

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
                self._namespace = Class(sr.result, base_clause_visitor.base_clause, self._namespace)
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
        declaration.accept(self)

    def visit_function_definition(self, function_definition):
        # type: (ast.FunctionDefinition) -> None
        # look for class definitions in the decl-specifier-seq
        function_definition.accept_decl_specifier_seq(self)
        # also export declaration itself, if necessary
        # TODO


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
        "exports",
        help="Output export file",
        metavar="EXPORT",
    )

    arguments = argument_context.parse_args()
    results = pyxx.run(arguments)
    assert len(results) == 1

    explorer = Explorer(arguments.module)
    results[0].accept(explorer)

    with open(arguments.out, 'w') as out:
        out.write('#include <motor/meta/typeinfo.hh>\n'
                  '#include "%s"\n'
                  '#include <motor/meta/engine/operatortable.meta.hh>\n'
                  '%s\n\n' % (arguments.in_relative, '\n'.join('#include %s' % i for i in results[0]._included_files)))
        explorer._namespace.write_declarations([], out)
        explorer._namespace.write_metaclasses([], out)

    with open(arguments.doc, 'w') as doc:
        pass

    with open(arguments.exports, 'wb') as exports:
        pickle.dump((arguments.module, arguments.root, arguments.in_relative), exports)
        explorer._namespace.dump_exports([], exports)
