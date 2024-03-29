import os
import sys
import re
import pickle
from typing import IO, List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'vendor'))
import kernel_support
import pyxx
from pyxx import ast, utils


def underscore_to_camelcase(value: str) -> str:
    return ''.join(x.capitalize() or '_' for x in value.split('_'))


class ArgumentDeclarationVisitor(utils.StringRef):

    def __init__(self) -> None:
        utils.StringRef.__init__(self)
        self._depth = 0
        self.name_position = (0, 0)

    def visit_declarator_element_abstract(self, declarator_element_abstract: ast.DeclaratorElementAbstract) -> None:
        if self._depth == 1:
            assert False  # parameter needs to have a name for the exporter
        else:
            return utils.StringRef.visit_declarator_element_abstract(self, declarator_element_abstract)

    def visit_declarator_element_abstract_pack(
            self, declarator_element_abstract_pack: ast.DeclaratorElementAbstractPack
    ) -> None:
        if self._depth == 1:
            assert False  # parameter pack not supported
        else:
            return utils.StringRef.visit_declarator_element_abstract_pack(self, declarator_element_abstract_pack)

    def visit_declarator_element_pack_id(self, declarator_element_pack_id: ast.DeclaratorElementPackId) -> None:
        if self._depth == 1:
            assert False  # parameter pack not supported
        else:
            return utils.StringRef.visit_declarator_element_pack_id(self, declarator_element_pack_id)

    def visit_declarator_element_id(self, declarator_element_id: ast.DeclaratorElementId) -> None:
        p1 = len(self.result)
        utils.StringRef.visit_declarator_element_id(self, declarator_element_id)
        if self._depth == 1:
            self.name_position = (p1, len(self.result))

    def visit_parameter_declaration(self, parameter_declaration: ast.ParameterDeclaration) -> None:
        self._depth += 1
        utils.StringRef.visit_parameter_declaration(self, parameter_declaration)
        self._depth -= 1


class DeclarationVisitor(ast.Visitor):

    def __init__(self, namespace: kernel_support.KernelNamespace, decl_specifier_seq: ast.DeclSpecifierSeq) -> None:
        self._decl_specifier_seq = decl_specifier_seq
        self._declaration_namespace = namespace
        self._current_namespace = namespace
        self._current_name = ''
        self._current_parameters = []  # type: List[Tuple[str, Tuple[int, int]]]

    def visit_decl_specifier_seq(self, decl_specifier_seq: ast.DeclSpecifierSeq) -> None:
        decl_specifier_seq.accept_type_specifier_seq(self)

    def visit_type_specifier_seq(self, type_specifier_seq: ast.TypeSpecifierSeq) -> None:
        if len(type_specifier_seq.types) != 1:
            assert False  # error: kernel should return void
        elif type_specifier_seq.types[0] != ast.type.PrimitiveTypeSpecifiers.VOID:
            assert False  # error: kernel should return void

    def visit_ambiguous_init_declarator_list(
            self, ambiguous_init_declarator_list: ast.AmbiguousInitDeclaratorList
    ) -> None:
        ambiguous_init_declarator_list.accept_best(self)

    def visit_init_declarator_list(self, init_declarator_list: ast.InitDeclaratorList) -> None:
        init_declarator_list.accept_init_declarators(self)

    def visit_ambiguous_init_declarator(self, ambiguous_init_declarator: ast.AmbiguousInitDeclarator) -> None:
        pass

    def visit_init_declarator(self, init_declarator: ast.InitDeclarator) -> None:
        init_declarator.accept_declarator(self)

    def visit_member_init_declarator(self, member_init_declarator: ast.MemberInitDeclarator) -> None:
        member_init_declarator.accept_declarator(self)

    def visit_declarator_list(self, declarator_list: ast.DeclaratorList) -> None:
        if not declarator_list.is_method():
            assert False  # todo: error
        declarator_list.accept_element(self)

    def visit_declarator_element_id(self, declarator_element_id: ast.DeclaratorElementId) -> None:
        declarator_element_id.accept_name(self)

    def visit_declarator_element_pack_id(self, declarator_element_pack_id: ast.DeclaratorElementPackId) -> None:
        # todo: proper error message
        assert False

    def visit_declarator_element_abstract(self, declarator_element_abstract: ast.DeclaratorElementAbstract) -> None:
        assert False

    def visit_declarator_element_abstract_pack(
            self, declarator_element_abstract_pack: ast.DeclaratorElementAbstractPack
    ) -> None:
        assert False

    def visit_declarator_element_group(self, declarator_element_group: ast.DeclaratorElementGroup) -> None:
        declarator_element_group.accept_next(self)

    def visit_declarator_element_pointer(self, declarator_element_pointer: ast.DeclaratorElementPointer) -> None:
        # todo: proper error message
        assert False

    def visit_declarator_element_reference(self, declarator_element_reference: ast.DeclaratorElementReference) -> None:
        # todo: proper error message
        assert False

    def visit_declarator_element_rvalue_reference(
            self, declarator_element_rvalue_reference: ast.DeclaratorElementRValueReference
    ) -> None:
        # todo: proper error message
        assert False

    def visit_declarator_element_array(self, declarator_element_array: ast.DeclaratorElementArray) -> None:
        # todo: proper error message
        assert False

    def visit_declarator_element_method(self, declarator_element_method: ast.DeclaratorElementMethod) -> None:
        # first, accept the name
        declarator_element_method.accept_next(self)
        declarator_element_method.accept_parameter_clause(self)
        assert self._current_name != ''
        if self._current_name not in self._current_namespace.kernels:
            self._current_namespace.kernels[self._current_name] = kernel_support.Kernel(self._current_parameters)
        self._current_namespace = self._declaration_namespace
        self._current_name = ''
        self._current_parameters = []

    def visit_ambiguous_parameter_clause(self, ambiguous_parameter_clause: ast.AmbiguousParameterClause) -> None:
        ambiguous_parameter_clause.accept_first(self)

    def visit_simple_parameter_clause(self, simple_parameter_clause: ast.SimpleParameterClause) -> None:
        if simple_parameter_clause.variadic:
            assert False  # not supported for kernel methods
        for i, parameter in enumerate(simple_parameter_clause.parameter_list):
            v = ArgumentDeclarationVisitor()
            parameter.accept(v)
            self._current_parameters.append((v.result, v.name_position))

    def visit_reference(self, reference: ast.Reference) -> None:
        for element in reference.name_list[:-1]:
            if isinstance(element, ast.RootId):
                pass
            sr = utils.StringRef()
            element.accept(sr)
            try:
                self._current_namespace = self._current_namespace.children[sr.result]
            except KeyError:
                ns = kernel_support.KernelNamespace()
                self._current_namespace.children[sr.result] = ns
                self._current_namespace = ns
        sr = utils.StringRef()
        reference.name_list[-1].accept(sr)
        self._current_name = sr.result

    def visit_typename_reference(self, typename_reference: ast.TypenameReference) -> None:
        assert False

    def visit_pack_expand_reference(self, pack_expand_reference: ast.PackExpandReference) -> None:
        assert False


class KernelCollector(pyxx.ast.Visitor):

    def __init__(self) -> None:
        self.root_namespace = kernel_support.KernelNamespace()
        self._namespace = [self.root_namespace]
        self._error_stack = []  # type: List[str]

    def visit_translation_unit(self, tu: ast.TranslationUnit) -> None:
        tu.accept_children(self)
        ns = filter_namespace(self.root_namespace)
        assert ns is not None
        self.root_namespace = ns

    def visit_namespace_declaration(self, namespace: ast.NamespaceDeclaration) -> None:
        if namespace.namespace_name is not None:
            for _, n in namespace.nested_name + [(False, namespace.namespace_name)]:
                try:
                    self._namespace.append(self._namespace[-1].children[n])
                except KeyError:
                    new_namespace = kernel_support.KernelNamespace()
                    self._namespace[-1].children[n] = new_namespace
                    self._namespace.append(new_namespace)
            namespace.accept_children(self)
            del self._namespace[-len(namespace.nested_name) - 1:]
        else:
            namespace.accept_children(self)

    def visit_using_directive(self, using_directive: ast.UsingDirective) -> None:
        self._namespace[-1].using_directives.append(using_directive)

    def visit_using_declaration(self, using_declaration: ast.UsingDeclaration) -> None:
        self._namespace[-1].using_declarations.append(using_declaration)

    def visit_ambiguous_declaration(self, ambiguous_declaration: ast.AmbiguousDeclaration) -> None:
        ambiguous_declaration.accept_first(self)

    def visit_simple_declaration(self, simple_declaration: ast.SimpleDeclaration) -> None:
        if simple_declaration.decl_specifier_seq is not None:
            for decl_specifier in simple_declaration.decl_specifier_seq.decl_specifiers:
                if decl_specifier.decl_specifier == '__kernel':
                    # collect kernel declarator
                    visitor = DeclarationVisitor(self._namespace[-1], simple_declaration.decl_specifier_seq)
                    simple_declaration.accept_decl_specifier_seq(visitor)
                    simple_declaration.accept_init_declarator_list(visitor)
                    break

        # look for class definitions in the decl-specifier-seq
        simple_declaration.accept_decl_specifier_seq(self)

    def visit_decl_specifier_seq(self, decl_specifier_seq: ast.DeclSpecifierSeq) -> None:
        # look for class definitions in the type specifiers of the decl-specifier-seq
        decl_specifier_seq.accept_type_specifier_seq(self)

    def visit_type_specifier_seq(self, type_specifier_seq: ast.TypeSpecifierSeq) -> None:
        # look for class definitions in the type specifiers
        type_specifier_seq.accept_types(self)

    def visit_class_specifier(self, class_specifier: ast.ClassSpecifier) -> None:
        self._error_stack.append('kernel functions cannot be class members')
        class_specifier.accept_members(self)
        self._error_stack.pop(-1)

    def visit_member_declaration(self, access_specifier: ast.AccessSpecifier, declaration: ast.Declaration) -> None:
        declaration.accept(self)

    def visit_function_definition(self, function_definition: ast.FunctionDefinition) -> None:
        if function_definition.decl_specifier_seq is not None:
            for decl_specifier in function_definition.decl_specifier_seq.decl_specifiers:
                if decl_specifier.decl_specifier == '__kernel':
                    visitor = DeclarationVisitor(self._namespace[-1], function_definition.decl_specifier_seq)
                    function_definition.accept_decl_specifier_seq(visitor)
                    function_definition.accept_declarator(visitor)
                    break

        # look for class definitions in the decl-specifier-seq
        function_definition.accept_decl_specifier_seq(self)


def filter_namespace(ns: kernel_support.KernelNamespace) -> Optional[kernel_support.KernelNamespace]:
    result = kernel_support.KernelNamespace()
    result.using_directives = ns.using_directives
    result.using_declarations = ns.using_declarations
    result.kernels = ns.kernels
    for name, sub_ns in ns.children.items():
        sub_ns_filtered = filter_namespace(sub_ns)
        if sub_ns_filtered is not None:
            result.children[name] = sub_ns_filtered
    if result.children or result.kernels:
        return result
    return None


def write_cc(
        capitalized_name: str,
        namespace: kernel_support.KernelNamespace,
        out_cc: IO[str],
        full_name: List[str]
) -> None:
    for name, ns in namespace.children.items():
        out_cc.write('namespace %s {\n' % name)
        write_cc(capitalized_name, ns, out_cc, full_name + [name])
        out_cc.write('}\n')

    if namespace.kernels:
        out_cc.write('\n')
        for kernel_name, kernel in namespace.kernels.items():
            parameter_type_names = [
                ('parameter_type_%d' % i, parameter[index[0]:index[1]])
                for i, (parameter, index) in enumerate(kernel.parameters[2:])
            ]
            argument_assign = '\n    ,   '.join(
                tuple('m_%s(%s)' % (arg[1], arg[1]) for arg in parameter_type_names) +
                tuple('%s(%s::create(Motor::Arena::task(), this))' % (arg[1], arg[0]) for arg in parameter_type_names)
            )
            format_parameters = {
                'Name':
                    capitalized_name,
                'kernel_full_name':
                    '.'.join(full_name + [underscore_to_camelcase(kernel_name)]),
                'kernelName':
                    kernel_name,
                'KernelName':
                    underscore_to_camelcase(kernel_name),
                'argument_count':
                    len(kernel.parameters) - 2,
                'argument_params':
                    ', '.join(('%s %s' % arg for arg in parameter_type_names)),
                'argument_assign':
                    argument_assign,
                'parameter_assign':
                    '    \n'.join(
                        [
                            'new(&parameters[%d]) ref< ::Motor::KernelScheduler::IParameter >('
                            'm_%s->producer()->getParameter(loader, m_%s));'
                            % (i, arg[1], arg[1]) for i, arg in enumerate(parameter_type_names)
                        ]
                    ),
                'parameter_save':
                    '    \n'.join(
                        [
                            'result->parameters[%d] = minitl::make_tuple(%s, parameters[%d]);' % (i, arg[1], i)
                            for i, arg in enumerate(parameter_type_names)
                        ]
                    ),
                'product_chain':
                    '    \n'.join(
                        [
                            'result->chain.push_back(::Motor::Task::ITask::CallbackConnection(\n'
                            '        m_%s->producer()->getTask(loader),\n'
                            '        task->startCallback())\n'
                            '    );' % arg[1] for arg in parameter_type_names
                        ]
                    )
            }
            out_cc.write(
                'static ref< ::Motor::KernelScheduler::Kernel > s_%(KernelName)sKernel =\n'
                '    ref< ::Motor::KernelScheduler::Kernel >::create(\n'
                '        ::Motor::Arena::task(),\n'
                '        s_%(Name)sKernelCode,\n'
                '        ::Motor::istring("%(kernelName)s")\n'
                '    );\n'
                '\n'
                '%(KernelName)sKernel::PluginHook %(KernelName)sKernel::g_kernelHook =\n'
                '    %(KernelName)sKernel::PluginHook(\n'
                '        ::Motor::MOTOR_CONCAT(g_pluginHooks_, MOTOR_PROJECTID),\n'
                '        %(KernelName)sKernel::ResourceHook(s_%(KernelName)sKernel)\n'
                '    );\n'
                '\n'
                '%(KernelName)sKernel::%(KernelName)sKernel(%(argument_params)s)\n'
                '    :   %(argument_assign)s\n'
                '{\n'
                '}\n'
                '\n'
                '%(KernelName)sKernel::~%(KernelName)sKernel()\n'
                '{\n'
                '}\n'
                '\n'
                'scoped< ::Motor::KernelScheduler::Producer::Runtime > %(KernelName)sKernel::createRuntime(\n'
                '    weak< const ::Motor::KernelScheduler::ProducerLoader > loader\n'
                ') const\n'
                '{\n'
                '    motor_forceuse(loader);\n'
                '    void* memory = malloca(sizeof(ref< ::Motor::KernelScheduler::IParameter >)*%(argument_count)s);\n'
                '    ref< ::Motor::KernelScheduler::IParameter >* parameters =\n'
                '        reinterpret_cast< ref< ::Motor::KernelScheduler::IParameter >*>(memory);\n'
                '    %(parameter_assign)s\n'
                '    ref< ::Motor::Task::KernelTask > task = ref< ::Motor::Task::KernelTask >::create(\n'
                '            ::Motor::Arena::task(),\n'
                '            ::Motor::istring("%(kernel_full_name)s"),\n'
                '            Motor::KernelScheduler::GPUType,\n'
                '            knl::Colors::Red::Red,\n'
                '            s_%(KernelName)sKernel,\n'
                '            parameters, parameters + %(argument_count)s\n'
                '        );\n'
                '    scoped< ::Motor::KernelScheduler::Producer::Runtime > result =\n'
                '        scoped< ::Motor::KernelScheduler::Producer::Runtime >::create(\n'
                '            ::Motor::Arena::task(), task, %(argument_count)s\n'
                '        );\n'
                '    %(parameter_save)s\n'
                '    %(product_chain)s\n'
                '    for (u32 i = 0; i < %(argument_count)s; ++i)\n'
                '        parameters[i].~ref();\n'
                '    freea(memory);\n'
                '    return result;\n'
                '}\n'
                '\n' % format_parameters
            )


def write_hh(
        namespace: kernel_support.KernelNamespace,
        out_hh: IO[str],
        full_name: List[str]
) -> None:
    if namespace.using_directives:
        out_hh.write('\n')
        for using_directive in namespace.using_directives:
            sr = utils.StringRef()
            using_directive.accept_reference(sr)
            out_hh.write('using namespace %s;\n' % sr.result)

    if namespace.using_declarations:
        out_hh.write('\n')
        for using_declaration in namespace.using_declarations:
            for reference in using_declaration.reference_list:
                sr = utils.StringRef()
                reference.accept(sr)
                out_hh.write('using %s;\n' % sr.result)

    for name, ns in namespace.children.items():
        out_hh.write('namespace %s {\n' % name)
        write_hh(ns, out_hh, full_name + [name])
        out_hh.write('}\n')

    if namespace.kernels:
        out_hh.write('\n')
        for kernel_name, kernel in namespace.kernels.items():
            argument_types = (
                '\n    '.join(
                    [
                        'typedef %skernel_type_%d%s;' % (parameter[:index[0]], i, parameter[index[1]:])
                        for i, (parameter, index) in enumerate(kernel.parameters[2:])
                    ] + [
                        'typedef ref< const ::Motor::KernelScheduler::Product< '
                        '::Motor::KernelScheduler::ParamTypeToKernelType< kernel_type_%d >::Type > > parameter_type_%d;'
                        % (i, i) for i in range(0,
                                                len(kernel.parameters) - 2)
                    ]
                )
            )
            parameter_type_names = [
                ('parameter_type_%d' % i, parameter[index[0]:index[1]])
                for i, (parameter, index) in enumerate(kernel.parameters[2:])
            ]
            format_parameters = {
                'argument_types':
                    argument_types,
                'kernel_full_name':
                    '.'.join(full_name + [underscore_to_camelcase(kernel_name)]),
                'kernelName':
                    kernel_name,
                'KernelName':
                    underscore_to_camelcase(kernel_name),
                'argument_count':
                    len(kernel.parameters),
                'argument_field':
                    '\n    '.join(('%s const m_%s;' % arg for arg in parameter_type_names)),
                'argument_result_assign':
                    '\n    '.join(
                        ('result[%d] = m_%s->parameter();' % (i, p[1]) for i, p in enumerate(parameter_type_names))
                    ),
                'argument_outs':
                    '\n    '.join(('[[motor::meta]] %s const %s;' % arg for arg in parameter_type_names)),
                'argument_params':
                    ', '.join(('%s %s' % arg for arg in parameter_type_names)),
            }
            out_hh.write(
                '\n'
                'class %(KernelName)sKernel : public ::Motor::KernelScheduler::Producer\n'
                '{\n'
                'private:\n'
                '    %(argument_types)s\n'
                'private:\n'
                '    %(argument_field)s\n'
                'private:\n'
                '    typedef ::Motor::Plugin::ResourceHook< ::Motor::KernelScheduler::Kernel > ResourceHook;\n'
                '    typedef ::Motor::Plugin::PluginHook< ResourceHook > PluginHook;\n'
                '    MOTOR_EXPORT static PluginHook g_kernelHook;\n'
                '\n'
                '    virtual scoped< ::Motor::KernelScheduler::Producer::Runtime > createRuntime(\n'
                '        weak< const ::Motor::KernelScheduler::ProducerLoader > loader\n'
                '    ) const override;\n'
                '\n'
                'public:\n'
                '    %(argument_outs)s\n\n'
                '    [[motor::meta]] %(KernelName)sKernel(%(argument_params)s);\n'
                '    ~%(KernelName)sKernel();\n'
                '};\n' % format_parameters
            )


if __name__ == '__main__':
    argument_context = pyxx.init_arguments()
    argument_context.add_argument(
        "-p", "--pch", dest="pch", help="Insert an include for precompiled header at the start of the file"
    )
    argument_context.add_argument("-m", "--module", dest="module", help="Module root")
    argument_context.add_argument("-n", "--name", dest="name", help="Kernel name")
    argument_context.add_argument(
        "out_kernel",
        help="Output kernel file",
        metavar="OUT_KERNEL",
    )
    argument_context.add_argument(
        "out_cc",
        help="Output C++ source file",
        metavar="OUT_CC",
    )
    argument_context.add_argument(
        "out_hh",
        help="Output C++ header file",
        metavar="OUT_HH",
    )
    argument_context.add_argument(
        "rel_hh",
        help="Relative path to header file",
        metavar="REL_HH",
    )

    arguments = argument_context.parse_args()
    results = pyxx.run(arguments)
    assert len(results) == 1
    translation_unit = results[0]
    collector = KernelCollector()
    collector.visit_translation_unit(translation_unit)
    with open(arguments.out_kernel, 'wb') as out_kernel:
        pickle.dump(collector.root_namespace, out_kernel)

    Name = ''.join([x.capitalize() for x in arguments.name.split('.')])
    with open(arguments.out_cc, 'w') as source_file:
        source_file.write(
            '#include "%s"\n'
            'namespace Motor\n'
            '{\n'
            '\n'
            'extern Plugin::HookList MOTOR_CONCAT(g_pluginHooks_, MOTOR_PROJECTID);\n'
            '\n'
            '}\n'
            '\n'
            % arguments.rel_hh
        )
        source_file.write(
            'static ref< ::Motor::KernelScheduler::Code > s_%(Name)sKernelCode =\n'
            '    ref< ::Motor::KernelScheduler::Code >::create(\n'
            '        ::Motor::Arena::task(),\n'
            '        ::Motor::inamespace("%(plugin)s.%(kernel_full_name)s")\n'
            '    );\n' % {
                'Name': Name,
                'plugin': arguments.module,
                'kernel_full_name': arguments.name
            }
        )
        source_file.write(
            'MOTOR_EXPORT\n'
            '::Motor::Plugin::PluginHook<\n'
            '        Motor::Plugin::ResourceHook< ::Motor::KernelScheduler::Code >\n'
            '    > g_%(Name)sKernelHook =\n'
            '    ::Motor::Plugin::PluginHook< ::Motor::Plugin::ResourceHook< ::Motor::KernelScheduler::Code > >(\n'
            '        ::Motor::MOTOR_CONCAT(g_pluginHooks_, MOTOR_PROJECTID),\n'
            '        ::Motor::Plugin::ResourceHook< ::Motor::KernelScheduler::Code >(s_%(Name)sKernelCode)\n'
            '    );\n' % {'Name': Name}
        )
        source_file.write('\n')

        write_cc(Name, collector.root_namespace, source_file, [])

    with open(arguments.out_hh, 'w') as header_file:
        plugin = re.sub('[^a-zA-Z0-9_]+', '_', arguments.module).upper()
        header = re.sub('[^a-zA-Z0-9_]+', '_', arguments.rel_hh).upper()
        header_file.write(
            '/* Motor <motor.devel@gmail.com>\n'
            '   see LICENSE for detail */\n'
            '#ifndef %s_%s\n'
            '#define %s_%s\n'
            '\n'
            '#include    <motor/scheduler/kernel/kernel.meta.hh>\n'
            '#include    <motor/scheduler/task/itask.hh>\n'
            '#include    <motor/scheduler/kernel/product.meta.hh>\n'
            '#include    <motor/scheduler/kernel/producer.meta.hh>\n'
            '#include    <motor/scheduler/kernel/producerloader.hh>\n'
            '#include    <motor/scheduler/kernel/parameters/parameters.hh>\n'
            '#include    <motor/scheduler/task/kerneltask.hh>\n'
            '#include    <motor/kernel/colors.hh>\n'
            '#include    <motor/plugin/resourcehook.hh>\n'
            '\n' % (plugin, header, plugin, header)
        )
        for include in translation_unit.included_files:
            header_file.write('#include %s\n' % include)
        write_hh(collector.root_namespace, header_file, [])
        header_file.write('\n#include <%s.factory.hh>\n#endif\n' % os.path.splitext(arguments.rel_hh)[0])
