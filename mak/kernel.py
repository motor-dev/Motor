import sys
import cpp
import os

from optparse import OptionParser

options = OptionParser()
options.set_usage('kernel.py input output')

global_macro_map = {
    "__declspec": True,
    "__attribute__": True,
    "CALLBACK": False,
    "WINAPI": False,
    "__cdecl": False,
    "__fastcall": False,
    "__stdcall": False,
    "PASCAL": False,
}

def split_type(name):
    name = name.strip()
    template_begin = name.find('<')
    if template_begin == -1:
        raise Exception('invalid kernel input type: %s' % name)
    template_name = name[0:template_begin].strip()
    type_name = name[template_begin+1:-1].strip()
    if template_name not in ['in', 'out', 'inout']:
        raise Exception('invalid kernel input type: %s' % name)
    return (template_name, type_name)

def doParse(source, output, temppath, macro = [], macrofile = [], pch="", name=""):
    with open(output, 'w') as implementation:
        kernel_name = os.path.splitext(os.path.splitext(os.path.basename(output))[0])[0]
        fullname = [i.capitalize() for i in name.split('_')] + [kernel_name.capitalize()]
        idname = [i for i in name.split('_')] + [kernel_name]
        implementation.write('/* BugEngine <bugengine.devel@gmail.com> / 2008-2014\n')
        implementation.write('   see LICENSE for detail */\n\n')
        implementation.write('#ifndef BE_%s_%s_SCRIPT_HH_\n'%(name.upper(), kernel_name.upper()))
        implementation.write('#define BE_%s_%s_SCRIPT_HH_\n'%(name.upper(), kernel_name.upper()))
        implementation.write('/**************************************************************************************************/\n')
        if pch:
            implementation.write("#include    <%s>\n" % pch)
        implementation.write('#include    <scheduler/kernel/kernel.script.hh>\n')
        implementation.write('#include    <scheduler/task/itask.hh>\n')
        implementation.write('#include    <scheduler/kernel/product.hh>\n')
        implementation.write('#include    <scheduler/task/kerneltask.hh>\n')
        implementation.write('#include    <kernel/colors.hh>\n')
        lexer = cpp.lex.lex(module=cpp.lexer)
        lexer.inside = 0
        lexer.sourcename = source
        lexer.error = 0
        lexer.output = implementation
        yacc = cpp.parser.Parser(output, '', '', name, source, pch)

        lexer.macro_map = dict(global_macro_map)
        if macro:
            for m in macro:
                if m.endswith('()'):
                    lexer.macro_map[m[:-2].strip()] = True
                else:
                    lexer.macro_map[m.strip()] = False
        if macrofile:
            for f in macrofile:
                try:
                    macros = open(f, 'r')
                except IOError as e:
                    raise Exception("cannot open macro file %s : %s" % (f, str(e)))
                for m in macros.readlines():
                    m = m.strip()
                    if m.endswith('()'):
                        lexer.macro_map[m[:-2].strip()] = True
                    else:
                        lexer.macro_map[m.strip()] = False

        try:
            input = open(source, 'r')
        except IOError as e:
            raise Exception("cannot open input file %s : %s" % (source, str(e)))


        try:
            yacc.parse(input.read(), lexer=lexer)
            input.close()

            if lexer.error != 0:
                return lexer.error
        except:
            return 1

        try:
            m = yacc.root.members.methods['kmain']
        except KeyError:
            raise Exception("could not locate method kmain in kernel")
        if len(m) > 1:
            raise Exception("cannot overload metod kmain")
        m = m[0]
        arguments = []
        arg0 = m.value.args.args[0]
        if arg0.type != 'u32' and arg0.type != 'const u32':
            raise Exception("invalid signature for method kmain")
        arg1 = m.value.args.args[1]
        if arg1.type != 'u32' and arg1.type != 'const u32':
            raise Exception("invalid signature for method kmain")
        for arg in m.value.args.args[2:]:
            template_name, type_name = split_type(arg.type)
            arguments.append((arg.name, type_name, template_name))

        implementation.write('\n')
        #for ns in fullname[:-1]:
        #	implementation.write('namespace %s { ' % ns)
        implementation.write('namespace Kernels\n{\n\n')
        implementation.write('class %s : public BugEngine::Kernel::KernelDescription\n{\n' % fullname[-1])
        implementation.write('private:\n')
        for arg_name, arg_type, input_type in arguments:
            implementation.write('    BugEngine::Kernel::Product< %s > const m_%s;\n' % (arg_type, arg_name))
        implementation.write('    scoped< BugEngine::Task::ITask > const m_kernelTask;\n')
        for arg_name, arg_type, input_type in arguments:
            if input_type in ['in', 'inout']:
                implementation.write('    BugEngine::Task::ITask::CallbackConnection const m_%sChain;\n' % (arg_name))
        implementation.write('private:\n')
        implementation.write('    minitl::array< weak<const BugEngine::Kernel::IStream> > makeParameters() const\n')
        implementation.write('    {\n')
        implementation.write('        minitl::array< weak<const BugEngine::Kernel::IStream> > result(BugEngine::Arena::task(), %d);\n' % len(arguments))
        i = 0
        for arg_name, arg_type, input_type in arguments:
            implementation.write('        result[%d] = m_%s.stream;\n' % (i, arg_name))
            i += 1
        implementation.write('        return result;\n')
        implementation.write('    }\n')
        implementation.write('published:\n')
        for arg_name, arg_type, input_type in arguments:
            if input_type in ['out', 'inout']:
                implementation.write('    BugEngine::Kernel::Product< %s > const %s;\n' % (arg_type, arg_name))
        implementation.write('published:\n')
        implementation.write('    %s(' % fullname[-1])
        implementation.write(', '.join(['const BugEngine::Kernel::Product< %s >& %s'%(arg_type, arg_name) for arg_name, arg_type, input_type in arguments if input_type in ['in', 'inout']]))
        implementation.write(')\n')
        implementation.write('        :   KernelDescription("%s")\n        ,   ' % '.'.join(idname))
        for arg_name, arg_type, input_type in arguments:
            if input_type in ['in', 'inout']:
                implementation.write('m_%s(%s)\n        ,   ' % (arg_name, arg_name))
            else:
                raise Exception('not implemented')
        implementation.write('m_kernelTask(scoped<BugEngine::Task::KernelTask>::create(BugEngine::Arena::general(), "%s", BugEngine::Colors::Red::Red, BugEngine::Scheduler::High, this, makeParameters()))' % '.'.join(idname))
        if arguments:
            implementation.write('\n        ,   ')
            implementation.write('\n        ,   '.join(['m_%sChain(%s.producer, m_kernelTask->startCallback())' % (arg_name, arg_name) for arg_name, arg_type, inout_type in arguments if input_type in ['in', 'inout']]))
        for arg_name, arg_type, input_type in arguments:
            if input_type == 'inout':
                implementation.write('\n        ,   %s(%s.stream, m_kernelTask)' % (arg_name, arg_name))
            elif input_type == 'out':
                raise Exception('not implemented')
        implementation.write('\n    {\n    }\n')
        implementation.write('};\n\n')
        implementation.write('}')
        implementation.write('\n\n/**************************************************************************************************/\n')
        implementation.write('#endif\n')

    return 0

if __name__ == '__main__':
    (options, args) = options.parse_args()
    if len(args) != 2:
        options.print_help()
        exit(1)
    else:
        with open(args[1], 'w'):
            pass
        exit(0)
