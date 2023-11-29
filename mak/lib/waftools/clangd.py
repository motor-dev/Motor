import re
import build_framework
import waflib.ConfigSet
import waflib.Errors
import waflib.Task
import waflib.TaskGen
import waflib.Utils
import waftools_common.utils
from typing import List, Optional

_PATTERN = re.compile(r'\${([^}]+)}')


def _expand_cmd(input_task: waflib.Task.Task, env: waflib.ConfigSet.ConfigSet) -> List[str]:
    def get_var(name: str) -> str:
        if name == 'SRC':
            return 'task.inputs'
        elif name == 'TGT':
            return 'task.outputs'
        else:
            return 'Utils.to_list(env.%s)' % name

    def expand_var(match: re.Match[str]) -> str:
        # bring task into locals()
        task = input_task
        expression = match.group(1)
        expansion = expression.find(':')
        if expansion != -1:
            radix = env[expression[:expansion]]
            expression = expression[expansion + 1:]
        else:
            radix = '%s'
        execution = expression.find('.')
        if execution != -1:
            var = expression[:execution]
            code = expression[execution:]
        else:
            var = expression
            code = ''
        subvalue = var.find('[')
        if subvalue != -1:
            index = var[subvalue:]
            var = get_var(var[:subvalue])
            var = var + index
        else:
            var = get_var(var)
        var = eval(var + code, locals(), globals())
        if var:
            return ' '.join(radix % x for x in waflib.Utils.to_list(var))
        else:
            return ''

    cmd = _PATTERN.sub(expand_var, input_task.orig_run_str).split()
    return cmd


class clangd(build_framework.ProjectGenerator):
    """creates clangd compile_commands.json"""
    cmd = 'clangd'
    variant = 'clangd'

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = [self.__class__.cmd]

        self.env.VARIANT = '${Variant}'
        self.env.TOOLCHAIN = '${Toolchain}'
        self.env.PREFIX = '${Prefix}'
        self.env.TMPDIR = '${TmpDir}'
        self.env.DEPLOY_ROOTDIR = '${Deploy_RootDir}'
        self.env.DEPLOY_BINDIR = '${Deploy_BinDir}'
        self.env.DEPLOY_RUNBINDIR = '${Deploy_RunBinDir}'
        self.env.DEPLOY_LIBDIR = '${Deploy_LibDir}'
        self.env.DEPLOY_INCLUDEDIR = '${Deploy_IncludeDir}'
        self.env.DEPLOY_DATADIR = '${Deploy_DataDir}'
        self.env.DEPLOY_PLUGINDIR = '${Deploy_PluginDir}'
        self.env.DEPLOY_KERNELDIR = '${Deploy_KernelDir}'
        build_framework.add_feature(self, 'GUI')

    def execute(self) -> Optional[str]:
        result = build_framework.ProjectGenerator.execute(self)
        if result is not None:
            return result

        self.write_workspace()
        return None

    def write_workspace(self) -> None:
        clangd_node = self.srcnode.make_node('compile_commands.json')

        commands = []

        for g in self.groups:
            for tg in g:
                if not isinstance(tg, waflib.TaskGen.task_gen):
                    continue
                if 'kernel' not in tg.features:
                    tg.post()
                    for task in tg.tasks:
                        if task.__class__.__name__ in ('cxx', 'c', 'objc', 'objcxx'):
                            for env_name in self.env.ALL_TOOLCHAINS:
                                env = self.all_envs[env_name]
                                if env.SUB_TOOLCHAINS:
                                    bld_env = self.all_envs[env.SUB_TOOLCHAINS[0]].derive()
                                else:
                                    bld_env = env.derive()
                                includes, defines = waftools_common.utils.gather_includes_defines(tg)
                                if task.__class__.__name__ in ('cxx', 'objcxx'):
                                    bld_env.append_value(
                                        'INCPATHS', includes + bld_env.INCLUDES + bld_env.COMPILER_CXX_INCLUDES
                                    )
                                    bld_env.append_value('DEFINES', defines + bld_env.COMPILER_CXX_DEFINES)
                                else:
                                    bld_env.append_value(
                                        'INCPATHS', includes + bld_env.INCLUDES + bld_env.COMPILER_C_INCLUDES
                                    )
                                    bld_env.append_value('DEFINES', defines + bld_env.COMPILER_C_DEFINES)
                                cmd = _expand_cmd(task, bld_env)
                                for variant in self.env.ALL_VARIANTS:
                                    params = {'toolchain': env_name, 'optim': variant}
                                    commands.append(
                                        '\t{\n'
                                        '\t\t"directory": "%s",\n'
                                        '\t\t"arguments": [%s],\n'
                                        '\t\t"file": "%s",\n'
                                        '\t\t"output": "%s"\n'
                                        '\t}' % (
                                            task.get_cwd().abspath() % params,
                                            ", ".join('"%s"' % (c % params)
                                                      for c in cmd), task.inputs[0].abspath() % params,
                                            task.outputs[0].path_from(task.get_cwd()) % params
                                        )
                                    )
        with open(clangd_node.abspath(), 'w') as clangd_content:
            clangd_content.write('[\n')
            clangd_content.write(',\n'.join(commands))
            clangd_content.write('\n]')
