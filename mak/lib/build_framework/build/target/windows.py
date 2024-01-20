import coff
import waflib.Build
import waflib.Task
import waflib.Utils
import waflib.Errors
import waflib.TaskGen
import waflib.Tools.msvc
import waflib.Tools.ccroot
from .. import create_compiled_task, make_bld_node, external
from ...options import BuildContext


class symbols(waflib.Task.Task):
    """
    extract all symbols
    """
    color = 'GREEN'

    def run(self) -> int:
        with open(self.outputs[0].abspath(), 'w') as export_file:
            if self.generator.env.CC_NAME not in ('msvc', 'clang_msvc'):
                export_file.write('asm (".section .drectve");\n')
            seen = set([])
            for input_path in self.inputs:
                coff_file = coff.Coff(input_path.abspath())
                for table in coff_file.symtables.values():
                    for symbol in table:
                        export_file.write('/* %s */\n' % (str(symbol)))
                        if symbol.storagecls == coff.IMAGE_SYM_CLASS_EXTERNAL and (
                                symbol.sectnum > 0
                        ) and symbol.name not in seen:
                            seen.add(symbol.name)
                            if self.generator.env.CC_NAME not in ('msvc', 'clang_msvc'):
                                if self.generator.env.ARCHITECTURE == 'i386':
                                    undecorated_name = symbol.name[1:]
                                else:
                                    undecorated_name = symbol.name
                                export_file.write('asm (".ascii \\" -export:%s\\"");\n' % undecorated_name)
                            else:
                                if not symbol.name.startswith('??_G'):  # scalar destructor
                                    export_file.write('#pragma comment(linker, "/export:%s")\n' % symbol.name)
        return 0


@waflib.TaskGen.feature('motor:export_all')
@waflib.TaskGen.after_method('process_source')
@waflib.TaskGen.before_method('apply_link')
def generate_export_file(self: waflib.TaskGen.task_gen) -> None:
    if self.env.DEST_BINFMT == 'pe':
        export_file = make_bld_node(self, 'src', '', 'exports.cc')
        self.create_task('symbols', [c.outputs[0] for c in getattr(self, 'compiled_tasks', [])], [export_file])
        create_compiled_task(self, 'cxx', export_file)


@waflib.TaskGen.feature('cshlib', 'cxxshlib')
@waflib.TaskGen.after_method('process_source')
@waflib.TaskGen.after_method('generate_def_file')
@waflib.TaskGen.after_method('apply_link')
def apply_def_flag(self: waflib.TaskGen.task_gen) -> None:
    if self.env.DEST_BINFMT == 'pe':
        for f in getattr(self, 'def_files', []):
            self.env.append_value('LINKFLAGS', [self.env.DEF_ST, f.abspath()])
            link_task = getattr(self, 'link_task')  # type: waflib.Task.Task
            link_task.dep_nodes.append(f)


@waflib.TaskGen.feature('cshlib', 'cxxshlib', 'cprogram', 'cxxprogram')
@waflib.TaskGen.after_method('apply_link')
@waflib.TaskGen.after_method('apply_flags_msvc')
def apply_implib(self: waflib.TaskGen.task_gen) -> None:
    if self.env.DEST_BINFMT == 'pe':
        target_name = self.target.split('/')[-1]
        target_file = self.env.implib_PATTERN % target_name
        link_task = getattr(self, 'link_task')  # type: waflib.Task.Task
        implib_node = link_task.outputs[0].parent.make_node(target_file)
        link_task.outputs.append(implib_node)
        if self.env.COMPILER_ABI == 'msvc':
            link_task.outputs.append(implib_node.change_ext('.exp'))
        link_task.env.append_value('LINKFLAGS', [self.env.IMPLIB_ST % implib_node.abspath()])


def setup_build_windows(build_context: BuildContext) -> None:
    build_context.platforms.append(external(build_context, 'motor.3rdparty.system.win32'))
    build_context.platforms.append(external(build_context, 'motor.3rdparty.system.dbghelp'))
