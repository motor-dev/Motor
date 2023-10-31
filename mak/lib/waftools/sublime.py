import sys
import waflib.Context
import waflib.TaskGen
import build_framework
from typing import Optional


class sublime3(build_framework.BuildContext):
    """creates workspace for Sublime Text"""
    cmd = 'sublime'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/sublime'

    # motor_variant = '%(motor_variant)s'

    def execute(self) -> Optional[str]:
        """
        Entry point
        """
        if build_framework.schedule_setup(self):
            return "SKIP"

        self.restore()
        if not self.all_envs:
            self.load_envs()
        self.variant = self.__class__.motor_variant
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

        self.recurse([self.run_dir])
        self.write_workspace()
        return None

    def write_workspace(self) -> None:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.srcnode.name)

        workspace_node = self.srcnode.make_node('%s.sublime-project' % appname)
        extra_node = self.motornode.make_node('extra')

        folders = []

        for g in self.groups:
            for tg in g:
                if not isinstance(tg, waflib.TaskGen.task_gen):
                    continue
                for _, node in getattr(tg, 'source_nodes'):
                    name = tg.name
                    path = node.path_from(self.srcnode).replace('\\', '/')
                    if node.is_child_of(extra_node):
                        while node.parent != extra_node:
                            node = node.parent
                        name += '[%s]' % node.name
                    folders.append('\t\t{\n\t\t\t"name": "%s",\n\t\t\t"path": "%s"\n\t\t}' % (name, path))

        systems = []
        for env_name in self.env.ALL_TOOLCHAINS:
            for variant in self.env.ALL_VARIANTS:
                systems.append(
                    '\t\t{\n'
                    '\t\t\t"name": "%s - %s",\n'
                    '\t\t\t"cmd": ["%s", "%s", "build:%s:%s"]\n'
                    '\t\t}' % (env_name, variant, sys.executable, sys.argv[0], env_name, variant)
                )

        with open(workspace_node.abspath(), 'w') as workspace:
            workspace.write('{\n\t"folders":\n\t[\n')
            workspace.write(',\n'.join(folders))
            workspace.write(
                '\n'
                '\t],\n'
                '\t"settings":\n'
                '\t{\n'
                '\t\t"LSP":\n'
                '\t\t{\n'
                '\t\t\t"pyls":\n'
                '\t\t\t{\n'
                '\t\t\t\t"enabled": true\n'
                '\t\t\t},\n'
                '\t\t\t"clangd":\n'
                '\t\t\t{\n'
                '\t\t\t\t"enabled": true\n'
                '\t\t\t}\n'
                '\t\t}\n'
                '\t},\n'
                '\t"build_systems":\n'
                '\t[\n'
                '%s'
                '\t]\n'
                '}\n' % (',\n'.join(systems))
            )
