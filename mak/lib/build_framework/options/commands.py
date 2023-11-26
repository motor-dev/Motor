import os
import sys
import pickle
import waflib.ConfigSet
import waflib.Configure
import waflib.Options
import waflib.Context
import waflib.Logs
import waflib.Utils
import waflib.Errors
import waflib.Node
import waflib.Build
import waflib.Task
import waflib.TaskGen
from .display import clear_status_line

from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

T = TypeVar('T', bound=waflib.Context.Context)

OptionsContext = waflib.Options.OptionsContext

# cache option context to use in file change detection
OPTION_CONTEXT = None  # type: Optional[waflib.Options.OptionsContext]

KernelProcessor = Callable[
    ["BuildContext", waflib.TaskGen.task_gen, List[str], waflib.Node.Node, waflib.Node.Node, str], None]

task_uid = waflib.Task.Task.uid


def new_task_uid(task: waflib.Task.Task) -> Tuple[str, bytes]:
    return getattr(task.generator, 'group', ''), task_uid(task)


setattr(waflib.Task.Task, 'uid', new_task_uid)


def autoreconfigure(execute_method: Callable[[T], Optional[str]]) -> Callable[[T], Optional[str]]:
    """
        Decorator used to set the commands that can be reconfigured automatically
    """

    def execute(self: T) -> Optional[str]:
        """
            First check if reconfiguration is needed, then triggers the
            normal execute.
        """
        env = waflib.ConfigSet.ConfigSet()
        do_config = False
        try:
            env.load(os.path.join(waflib.Context.top_dir, waflib.Options.lockfile))
        except IOError:
            raise waflib.Errors.WafError('The project was not configured: run "waf configure" first!')
        else:
            if env.run_dir != waflib.Context.run_dir:
                do_config = True
            else:
                hash_value = 0     # type: Union[bytes, int]
                for filename in env.files:
                    try:
                        hash_value = waflib.Utils.h_list((hash_value, waflib.Utils.readf(filename, 'rb')))
                    except IOError:
                        do_config = True
                do_config = do_config or (hash_value != env.hash)

        clear_status_line(self)

        if do_config:
            waflib.Logs.warn('wscript files have changed; reconfiguring the project')
            waflib.Options.commands.insert(0, self.cmd)
            waflib.Options.commands.insert(0, 'reconfigure')
            return "SKIP"

        return execute_method(self)

    return execute


def schedule_setup(context: 'BuildContext') -> bool:
    """
        Checks if setup is needed, if so adds it to the list of commands
    """
    context.init_dirs()
    do_setup = False
    try:
        lock = waflib.ConfigSet.ConfigSet()
        lockfile = os.path.join(context.cache_dir, waflib.Options.lockfile + '.%s.setup' % context.motor_toolchain)
        lock.load(lockfile)
    except (AttributeError, IOError):
        waflib.Logs.warn('setup not run; setting up the toolchain')
        do_setup = True
    else:
        env = waflib.ConfigSet.ConfigSet()
        env.load(os.path.join(context.cache_dir, '%s_cache.py' % context.motor_toolchain))
        for option_name, value in env.SETUP_OPTIONS:
            new_value = getattr(waflib.Options.options, option_name)
            if new_value != value:
                do_setup = True
                waflib.Logs.warn(
                    'value of %s has changed (%s => %s); setting up the toolchain' % (option_name, value, new_value)
                )
        hash_value = 0     # type: Union[bytes, int]
        for filename in lock.files:
            try:
                hash_value = waflib.Utils.h_list((hash_value, waflib.Utils.readf(filename, 'rb')))
            except IOError:
                do_setup = True
        if hash_value != lock.hash:
            do_setup = True
            waflib.Logs.warn('wscript files have changed; setting up the toolchain')

    if do_setup:
        waflib.Options.commands.insert(0, context.cmd)
        waflib.Options.commands.insert(0, 'setup:%s' % context.motor_toolchain)
    return do_setup


def autosetup(execute_method: Callable[['BuildContext'], Optional[str]]) -> Callable[['BuildContext'], Optional[str]]:
    """
        Decorator used to set the commands that can be setup automatically
    """

    def execute(self: 'BuildContext') -> Optional[str]:
        if schedule_setup(self):
            return "SKIP"

        return execute_method(self)

    return execute


def _tidy_rm(node: waflib.Node.Node) -> None:
    col1 = waflib.Logs.colors.CYAN
    col2 = waflib.Logs.colors.NORMAL
    parent = node.parent
    waflib.Logs.info('{rm}     %s%s%s' % (col1, node, col2))
    node.delete(evict=True)
    if len(getattr(parent, 'children', {})) == 0:
        _tidy_rm(parent)


def tidy_build(execute_method: Callable[["BuildContext"], Optional[str]]) -> Callable[["BuildContext"], Optional[str]]:
    """
        Decorator used to set the commands that tidy up the build folders
    """

    def execute(context: "BuildContext") -> Optional[str]:
        try:
            result = execute_method(context)
        finally:
            clear_status_line(context)
        if waflib.Options.options.tidy == 'force' or (
            waflib.Options.options.tidy == 'auto' and waflib.Options.options.nomaster is False
            and waflib.Options.options.static is False and waflib.Options.options.dynamic is False
            and waflib.Options.options.targets == '' and waflib.Options.options.tests
        ):
            all_nodes = set(
                sum([context.bldnode.ant_glob('%s/**' % g, remove=False) for g in context.motor_groups[1:]], []) +
                context.srcnode.ant_glob(os.path.join(context.env.PREFIX, context.optim, '**'))
            )
            for group_name in context.motor_groups:
                all_nodes.discard(context.bldnode.make_node(group_name + waflib.Context.DBFILE))
            for group in context.groups:
                for task_gen in group:
                    install_task = getattr(task_gen, 'motor_install_task', None)
                    if install_task is not None:
                        for _, dest_file, _ in install_task.install_step:
                            all_nodes.discard(context.srcnode.make_node(dest_file))
                    for task in task_gen.tasks:
                        for output in task.outputs:
                            all_nodes.discard(output)
                        if task.__class__.__name__ == 'javac':
                            out_dir = getattr(task.generator, 'outdir', None)
                            if out_dir is not None:
                                for node in out_dir.ant_glob('**/*'):
                                    all_nodes.discard(node)
            for node in all_nodes:
                _tidy_rm(node)
        clear_status_line(context)
        return result

    return execute


class ConfigurationContext(waflib.Configure.ConfigurationContext):
    """
        ConfigurationContext subclass, which allows to store the current environment used
        for configure so it can be restored during a reconfigure.
    """
    optim = ''
    motor_toolchain = ''
    motor_variant = ''
    cmd = 'configure'

    def __init__(self, **kw: Any) -> None:
        waflib.Configure.ConfigurationContext.__init__(self, **kw)
        assert OPTION_CONTEXT is not None
        self.hash = OPTION_CONTEXT.hash
        self.files = OPTION_CONTEXT.files[:]
        self.common_env = self.env
        self.motornode = waflib.Node.Node('motor', None)

    def execute(self) -> Optional[str]:
        """
            Executes the configuration, then stores the current status that can be checked
            during the reconfiguration step
        """
        super(ConfigurationContext, self).execute()
        self.store_options()
        if waflib.Options.options.tidy == 'force' or (
            waflib.Options.options.tidy == 'auto' and waflib.Options.options.compilers == []
            and waflib.Options.options.platforms == []
        ):
            all_toolchains = self.bldnode.ant_glob('*', dir=True)
            for node in all_toolchains:
                if node.isdir():
                    if node.name not in [waflib.Build.CACHE_DIR, 'packages', 'projects'] + self.env.ALL_TOOLCHAINS:
                        _tidy_rm(node)
        return None

    def store_options(self) -> None:
        """
            Store last good configuration. This allows the build to automatically
            reconfigure when an environemnt variable changes, or a file changes on disc.
            The file will check common env variable as well as every wscript/python file
            loaded so far.
            Since this is called during the configuration step, the wscript/python files
            loaded during the build step only will not cause a reconfigure, which is the
            desired behaviour.
        """
        waflib.Options.options.environ = dict(os.environ)
        node = self.bldnode.make_node('options.pickle')
        pickle.dump(waflib.Options.options, open(node.abspath(), 'wb'), protocol=2)

    def store(self) -> None:
        """
            Cleans up the cache before storing more in there
        """
        for tool in waflib.Context.Context.tools.values():
            assert tool.__file__ is not None
            if tool.__file__ not in self.files:
                self.hash = waflib.Utils.h_list((self.hash, waflib.Utils.readf(tool.__file__, 'rb')))
                self.files.append(tool.__file__)

        for source in self.motornode.make_node('mak/lib/build_framework/options').ant_glob('**/*.py') + \
                      self.motornode.make_node('mak/lib/build_framework/configure').ant_glob('**/*.py'):
            if source.abspath() not in self.files:
                self.hash = waflib.Utils.h_list((self.hash, source.read('rb')))
                self.files.append(source.abspath())

        self.cachedir = self.bldnode.make_node(waflib.Build.CACHE_DIR)
        lst = self.cachedir.ant_glob('**', quiet=True)
        for x in lst:
            x.delete()

        waflib.Configure.ConfigurationContext.store(self)


class ReconfigurationContext(ConfigurationContext):
    """
        reconfigures the project with the same options as the last call to configure
    """
    cmd = 'reconfigure'

    def __init__(self, **kw: Any) -> None:
        super(ReconfigurationContext, self).__init__(**kw)

    def execute(self) -> Optional[str]:
        """
            restores the environment as it was during the last run, then reconfigures
            the project.
        """
        opt = waflib.Options.options
        self.restore_options()
        super(ReconfigurationContext, self).execute()
        waflib.Options.options = opt
        return None

    def restore_options(self) -> None:
        """
            Restores the environment as it was during the configure step. This allows
            reconfigure to discover the same compilers, even if the reconfigure step
            is not started in the same environment as configure (e.g. called from an IDE)
        """
        self.init_dirs()
        try:
            node = self.bldnode.make_node('options.pickle')
            waflib.Options.options = pickle.load(open(node.abspath(), 'rb'))
            os.environ.clear()
            os.environ.update(waflib.Options.options.environ)
            self.environ = dict(os.environ)
        except IOError:
            raise waflib.Errors.WafError('Option file not found; configure the project first')


class SetupContext(waflib.Configure.ConfigurationContext):
    motor_toolchain = ''
    motor_variant = ''
    cmd = '_setup'

    def __init__(self, **kw: Any) -> None:
        waflib.Configure.ConfigurationContext.__init__(self, **kw)
        assert OPTION_CONTEXT is not None
        self.motornode = waflib.Node.Node('motor', None)
        self.hash = OPTION_CONTEXT.hash
        self.files = OPTION_CONTEXT.files[:]
        self.common_env = self.env
        self.package_env = self.env
        self.package_node = self.motornode

    def load_envs(self) -> None:
        """
        The configuration command creates files of the form ``build/c4che/NAMEcache.py``. This method
        creates a :py:class:`waflib.ConfigSet.ConfigSet` instance for each ``NAME`` by reading those
        files and stores them in :py:attr:`waflib.Build.BuildContext.allenvs`.
        """
        setattr(self, 'cachedir', self.bldnode.find_node(waflib.Build.CACHE_DIR))
        if not self.cachedir:
            raise waflib.Errors.WafError('The project was not configured: run "waf configure" first!')
        lst = self.cachedir.ant_glob('**/*%s' % waflib.Build.CACHE_SUFFIX, quiet=True)

        if not lst:
            raise waflib.Errors.WafError('The cache directory is empty: reconfigure the project')

        for x in lst:
            name = x.path_from(self.cachedir).replace(waflib.Build.CACHE_SUFFIX, '').replace('\\', '/')
            env = waflib.ConfigSet.ConfigSet(x.abspath())
            self.all_envs[name] = env
            for f in env[waflib.Build.CFG_FILES]:
                newnode = self.root.find_resource(f)
                if not newnode or not newnode.exists():
                    raise waflib.Errors.WafError('Missing configuration file %r, reconfigure the project!' % f)

        self.common_env = self.env
        self.package_env = self.all_envs['packages']

    def setup(
        self,
        tool: Union[str, List[str]],
        tooldir: Optional[List[str]] = None,
        funs: Optional[List[str]] = None
    ) -> None:
        if isinstance(tool, list):
            for i in tool:
                self.setup(i, tooldir, funs)
            return

        module = waflib.Context.load_tool(tool, tooldir)
        if hasattr(module, "setup"):
            module.setup(self)
        self.tools.append({'tool': tool, 'tooldir': tooldir, 'funs': funs}) # type: ignore

    @autoreconfigure
    def execute(self) -> Optional[str]:
        self.init_dirs()

        self.load_envs()
        try:
            env = waflib.ConfigSet.ConfigSet(os.path.join(self.cachedir.abspath(), 'build.config.py'))
        except EnvironmentError:
            pass
        else:
            if env.version < waflib.Context.HEXVERSION:
                raise waflib.Errors.WafError(
                    'Project was configured with a different version of Waf, please reconfigure it'
                )

            for t in env.tools:
                self.setup(**t)

        path = os.path.join(self.bldnode.abspath(), 'setup-%s.log' % self.motor_variant)
        self.logger = waflib.Logs.make_logger(path, 'cfg')

        self.env = self.all_envs[self.motor_variant]
        self.recurse([waflib.Context.run_dir])
        self.store()
        env = waflib.ConfigSet.ConfigSet()
        env.files = self.files
        env.hash = self.hash
        env.store(
            os.path.join(
                self.bldnode.make_node(waflib.Build.CACHE_DIR).abspath(),
                waflib.Options.lockfile + '.%s.setup' % self.motor_toolchain
            )
        )
        clear_status_line(self)
        return None

    def store(self) -> None:
        for source in self.motornode.ant_glob('mak/lib/build_framework/setup/**/*', excl=['**/*.pyc']):
            if source.abspath() not in self.files:
                self.hash = waflib.Utils.h_list((self.hash, source.read('rb')))
                self.files.append(source.abspath())

        waflib.Configure.ConfigurationContext.store(self)


def add_setup_command(toolchain: str) -> None:

    class _(SetupContext):
        cmd = 'setup:%s' % toolchain
        motor_variant = toolchain
        motor_toolchain = toolchain
        variant = toolchain
        fun = 'multiarch_setup'


SAVED_ATTRS = 'node_sigs task_sigs imp_sigs raw_deps node_deps'.split()


class BuildContext(waflib.Build.BuildContext):
    optim = ''
    motor_toolchain = ''
    motor_variant = ''
    motor_optimisation = ''
    cmd = 'build'

    def __init__(self, **kw: Any) -> None:
        waflib.Build.BuildContext.__init__(self, **kw)
        self.motornode = waflib.Node.Node('motor', None)
        self.platforms = []            # type: List[str]
        self.package_env = waflib.ConfigSet.ConfigSet()
        self.package_node = self.motornode
        self.common_env = waflib.ConfigSet.ConfigSet()
        self.multiarch_envs = []       # type: List[waflib.ConfigSet.ConfigSet]
        self.kernel_processors = []    # type: List[KernelProcessor]
        self.launcher = None           # type: Optional[waflib.TaskGen.task_gen]
        self.pyxx_nodes = []           # type: List[waflib.Node.Node]
        self.post_mode = waflib.Build.POST_AT_ONCE
        self.motor_groups = ['', 'preprocess']
        if self.motor_variant:
            self.motor_groups.append(self.motor_variant)

    def get_variant_dir(self) -> str:
        return self.out_dir

    variant_dir = property(get_variant_dir, None)

    def load_envs(self) -> None:
        waflib.Build.BuildContext.load_envs(self)
        self.common_env = self.env
        self.package_env = self.all_envs['packages']
        for env in self.all_envs.values():
            env.OPTIM = self.optim
        self.env = self.all_envs[self.motor_toolchain + '.setup']

    @autoreconfigure
    @autosetup
    @tidy_build
    def execute(self) -> Optional[str]:
        try:
            result = waflib.Build.BuildContext.execute(self)
        finally:
            clear_status_line(self)
        return result

    def init_dirs(self) -> None:
        waflib.Build.BuildContext.init_dirs(self)
        self.motornode = self.path

    def store(self) -> None:
        data = {}                      # type: Dict[Any, Dict[Any, Any]]
        for group in self.motor_groups:
            data[group] = {
                'node_sigs': {},
                'task_sigs': {},
                'imp_sigs': {},
                'raw_deps': {},
                'node_deps': {},
            }
        for node, uid in self.node_sigs.items():
            data[uid[0]]['node_sigs'][str(node)] = uid
        for attr in 'task_sigs', 'imp_sigs', 'raw_deps':
            for uid, value in getattr(self, attr).items():
                data[uid[0]][attr][uid] = value
        attr = 'node_deps'
        for uid, value in getattr(self, attr).items():
            data[uid[0]][attr][uid] = [str(v) for v in value]

        for group in self.motor_groups:
            db = os.path.join(self.variant_dir, group + waflib.Context.DBFILE)
            x = pickle.dumps(data[group], waflib.Build.PROTOCOL)
            waflib.Utils.writef(db + '.tmp', x, m='wb')
            try:
                st = os.stat(db)
                os.remove(db)
                if not waflib.Utils.is_win32: # win32 has no chown but we're paranoid
                    os.chown(db + '.tmp', st.st_uid, st.st_gid)
            except (AttributeError, OSError):
                pass

            # do not use shutil.move (copy is not thread-safe)
            os.rename(db + '.tmp', db)

    def restore(self) -> None:
        cache = {}     # type: Dict[str, waflib.Node.Node]

        def get_node(node_name: str) -> waflib.Node.Node:
            try:
                node = cache[node_name]
            except KeyError:
                node = self.root.make_node(node_name)
                cache[node_name] = node
            return node

        try:
            env = waflib.ConfigSet.ConfigSet(os.path.join(self.cache_dir, 'build.config.py'))
        except EnvironmentError:
            pass
        else:
            if env.version < waflib.Context.HEXVERSION:
                raise waflib.Errors.WafError(
                    'Project was configured with a different version of Waf, please reconfigure it'
                )

            for t in env.tools:
                self.setup(**t)

        for group in self.motor_groups:
            dbfn = os.path.join(self.variant_dir, group + waflib.Context.DBFILE)
            try:
                file_data = waflib.Utils.readf(dbfn, 'rb')
            except (EnvironmentError, EOFError):
                # handle missing file/empty file
                waflib.Logs.debug('build: Could not load the build cache %s (missing)' % dbfn)
            else:
                try:
                    data = pickle.loads(file_data)
                except Exception as e:
                    waflib.Logs.debug('build: Could not pickle the build cache %s: %r' % (dbfn, e))
                else:
                    for attr, values in data.items():
                        x = getattr(self, attr)
                        if attr == 'node_sigs':
                            for node, uid in values.items():
                                x[get_node(node)] = uid
                        elif attr == 'node_deps':
                            for uid, nodes in values.items():
                                x[uid] = [get_node(n) for n in nodes]
                        else:
                            x.update(values)
        self.init_dirs()


class ProjectGenerator(BuildContext):

    pass


class CleanContext(BuildContext):
    optim = ''
    motor_toolchain = ''
    motor_variant = ''
    cmd = '_clean'

    def execute(self) -> Optional[str]:
        """
        See :py:func:`waflib.Build.BuildContext.execute`.
        """
        self.restore()
        if not self.all_envs:
            self.load_envs()

        self.recurse([self.run_dir])
        try:
            self.clean()
        finally:
            self.store()
            clear_status_line(self)
        return None

    def clean(self) -> None:
        waflib.Logs.debug('build: clean called')
        self.timer = waflib.Utils.Timer()

        if hasattr(self, 'clean_files'):
            for n in self.clean_files:
                n.delete()
        elif self.bldnode != self.srcnode:
            # would lead to a disaster if top == out
            lst = []   # type: List[waflib.Node.Node]
            for env in self.all_envs.values():
                lst.extend(self.root.find_or_declare(f) for f in env[waflib.Build.CFG_FILES])
            nodes = list(self.bldnode.ant_glob('**/*', excl='.lock* *conf_check_*/** config.log c4che/*', quiet=True))
            c = len(nodes)
            for i, n in enumerate(nodes):
                if n in lst:
                    continue
                n.delete()
                if self.progress_bar >= 1 and sys.stdout.isatty():
                    m = self.progress_line(i, c, waflib.Logs.colors.BLUE, waflib.Logs.colors.NORMAL)
                    self.set_status_line(m)
            if self.progress_bar >= 1 and sys.stdout.isatty():
                m = self.progress_line(c, c, waflib.Logs.colors.BLUE, waflib.Logs.colors.NORMAL)
                self.set_status_line(m)

        setattr(self.root, 'children', {})

        for v in waflib.Build.SAVED_ATTRS:
            if v == 'root':
                continue
            setattr(self, v, {})


class ListContext(waflib.Build.ListContext):
    optim = ''
    motor_toolchain = ''
    motor_variant = ''
    cmd = '_list'

    def execute(self) -> Optional[str]:
        try:
            result = waflib.Build.ListContext.execute(self)
        finally:
            clear_status_line(self)
        return result


def add_build_command(toolchain: str, optimisation: str) -> None:
    c = {}     # type: Dict[object, object]

    class BuildCommand(BuildContext):
        optim = optimisation
        cmd = 'build:' + toolchain + ':' + optimisation
        motor_toolchain = toolchain
        motor_variant = toolchain + '.' + optimisation
        variant = os.path.join(toolchain, optimisation)

    class CleanCommand(CleanContext):
        optim = optimisation
        cmd = 'clean:' + toolchain + ':' + optimisation
        motor_toolchain = toolchain
        motor_variant = toolchain + '.' + optimisation
        variant = os.path.join(toolchain, optimisation)

    class ListCommand(ListContext):
        optim = optimisation
        cmd = 'list:' + toolchain + ':' + optimisation
        motor_toolchain = toolchain
        motor_variant = toolchain + '.' + optimisation
        variant = os.path.join(toolchain, optimisation)

    c[waflib.Build.BuildContext] = BuildCommand
    c[waflib.Build.CleanContext] = CleanCommand
    c[waflib.Build.ListContext] = ListCommand


def add_all_build_commands(env: waflib.ConfigSet.ConfigSet) -> None:
    add_setup_command('projects')
    for toolchain in env.ALL_TOOLCHAINS:
        add_setup_command(toolchain)
        for optim in env.ALL_VARIANTS:
            add_build_command(toolchain, optim)


for command in ['build', 'clean']:
    for variant in ['debug', 'profile', 'final']:

        class BuildWrapperVariant(waflib.Build.BuildContext):
            cmd = '%s:all:%s' % (command, variant)

            def execute(self) -> Optional[str]:
                self.restore()
                if not self.all_envs:
                    self.load_envs()
                for toolchain in self.env.ALL_TOOLCHAINS:
                    build_cmd, _, build_variant = self.cmd.split(':')
                    waflib.Options.commands.append('%s:%s:%s' % (build_cmd, toolchain, build_variant))
                return None

    class BuildWrapperAll(waflib.Build.BuildContext):
        cmd = '%s:all' % command

        def execute(self) -> Optional[str]:
            self.restore()
            if not self.all_envs:
                self.load_envs()
            for toolchain in self.env.ALL_TOOLCHAINS:
                for build_variant in self.env.ALL_VARIANTS:
                    waflib.Options.commands.append('%s:%s:%s' % (self.cmd[:-4], toolchain, build_variant))
            return None


class ListToolchainsContext(waflib.Build.BuildContext):
    """
        Command that will print all available toolchains to stdout
    """
    cmd = 'list_toolchains'

    def execute(self) -> Optional[str]:
        self.restore()
        if not self.all_envs:
            self.load_envs()
        for toolchain in self.env.ALL_TOOLCHAINS:
            print(toolchain)
        return None


class ListVariantsContext(waflib.Build.BuildContext):
    """
        Command that will print all available variants to stdout
    """
    cmd = 'list_variants'

    def execute(self) -> Optional[str]:
        self.restore()
        if not self.all_envs:
            self.load_envs()
        for variant in self.env.ALL_VARIANTS:
            print(variant)
        return None


def options_commands(options_context: waflib.Options.OptionsContext) -> None:
    #    command.cmd = '_%s'%command.cmd
    global OPTION_CONTEXT
    OPTION_CONTEXT = options_context
    try:
        env = waflib.ConfigSet.ConfigSet('.waf_toolchains.cache')
        add_all_build_commands(env)
    except OSError:
        pass
