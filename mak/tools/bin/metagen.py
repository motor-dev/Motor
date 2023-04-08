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
        self._children = {}    # type: Dict[str, MetaObject]

    def dump_namespace(self, namespace, out):
        for name, child in self._children.items():
            namespace.append(name)
            child.dump_namespace(namespace, out)
            namespace.pop(-1)

    def write_metaclasses(self, namespace, out):
        for name, child in self._children.items():
            namespace.append(name)
            child.write_metaclasses(namespace, out)
            namespace.pop(-1)


class Namespace(MetaObject):

    def __init__(self, name: str, parent: MetaObject) -> None:
        super().__init__(parent)
        self._name = name
        parent._children[name] = self

    def dump_namespace(self, namespace, out):
        pickle.dump(namespace, out)
        super().dump_namespace(namespace, out)


class Class(MetaObject):

    def __init__(self, name: str, parent: MetaObject) -> None:
        super().__init__(parent)
        self._name = name
        parent._children[name] = self
        self._fields = []
        self._methods = []

    def write_metaclasses(self, namespace, out):
        full_name = '::'.join(namespace)
        out.write(
            'template<>\n'
            'MOTOR_EXPORT raw< const Motor::Meta::Class > Motor::Meta::ClassID<%s>::klass()\n'
            '{\n'
            '    return {nullptr};\n'
            '};\n'
            'template<>\n'
            'MOTOR_EXPORT Motor::istring Motor::Meta::ClassID<%s>::name()\n'
            '{\n'
            '    static const istring s_name("%s");\n'
            '    return s_name;\n'
            '};\n' % (full_name, full_name, namespace[-1])
        )


class Enum(Class):

    def __init__(self, name: str, parent: MetaObject) -> None:
        super().__init__(name, parent)


class Explorer(ast.Visitor):

    def __init__(self):
        self._namespace = MetaObject(None)

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
                self._namespace = Class(sr.result, self._namespace)
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
        metavar="OUT",
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
        "namespaces",
        help="Output namespace file",
        metavar="NS",
    )

    arguments = argument_context.parse_args()
    results = pyxx.run(arguments)
    assert len(results) == 1

    explorer = Explorer()
    results[0].accept(explorer)

    with open(arguments.out, 'w') as out:
        out.write('#include <motor/meta/typeinfo.hh>\n'
                  '#include "%s"\n\n' % arguments.in_relative)
        explorer._namespace.write_metaclasses([], out)

    with open(arguments.doc, 'w') as doc:
        pass

    with open(arguments.namespaces, 'wb') as ns:
        pickle.dump((arguments.module, arguments.root), ns)
        explorer._namespace.dump_namespace([], ns)
