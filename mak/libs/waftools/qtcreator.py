#! /Usr/bin/env python
# encoding: utf-8

import os
import sys
import re
import string
import datetime
from waflib import Context, Build, Logs, Options
from minixml import XmlDocument, XmlNode
from xml.dom.minidom import parse
import cmake

if sys.platform == 'win32':
    HOME_DIRECTORY = os.path.join(os.getenv('APPDATA'), 'QtProject', 'qtcreator')
    INI_FILE = os.path.join(os.getenv('APPDATA'), 'QtProject', 'QtCreator.ini')
else:
    HOME_DIRECTORY = os.path.join(os.path.expanduser('~'), '.config', 'QtProject', 'qtcreator')
    INI_FILE = os.path.join(os.path.expanduser('~'), '.config', 'QtProject', 'QtCreator.ini')
import hashlib

VAR_PATTERN = '${%s}' if sys.platform != 'win32' else '%%%s%%'

IGNORE_PATTERNS = [
    re.compile('.*\.pyc'),
    re.compile('.*__pycache__.*'),
]

CLANG_TIDY_CONFIG="ClangDiagnosticConfigs\\{0}\\clangTidyChecks=\n"\
                  "ClangDiagnosticConfigs\\{0}\\clangTidyChecksOptions=@Variant(\\0\\0\\0\\b\\0\\0\\0\\0)\n"\
                  "ClangDiagnosticConfigs\\{0}\\clangTidyMode=2\n"\
                  "ClangDiagnosticConfigs\\{0}\\clazyChecks=\n"\
                  "ClangDiagnosticConfigs\\{0}\\clazyMode=0\n"\
                  "ClangDiagnosticConfigs\\{0}\\diagnosticOptions=-w\n"\
                  "ClangDiagnosticConfigs\\{0}\\displayName=Motor\n"\
                  "ClangDiagnosticConfigs\\{0}\\id={{c75a31ba-e37d-4044-8825-36527d4ceea1}}\n"\
                  "ClangDiagnosticConfigs\\{0}\\useBuildSystemFlags=false\n"

def qbsArch(arch_name):
    archs = {'amd64': 'x86_64', 'x64': 'x86_64', 'x86_amd64': 'x86_64', 'aarch64': 'arm64'}
    return archs.get(arch_name, arch_name)


def qbsPlatform(env):
    if 'iphonesimulator' in env.VALID_PLATFORMS:
        return 'ios-simulator'
    elif 'iphone' in env.VALID_PLATFORMS:
        return 'ios'
    else:
        return env.VALID_PLATFORMS[0]


def qbsPlatformList(env):
    if 'iphonesimulator' in env.VALID_PLATFORMS:
        return '["ios-simulator","ios","darwin","bsd","unix"]'
    elif 'iphone' in env.VALID_PLATFORMS:
        return '["ios","darwin","bsd","unix"]'
    else:
        return None


def _hexdigest(s):
    """Return a string as a string of hex characters.
    """
    # NOTE:  This routine is a method in the Python 2.0 interface
    # of the native md5 module, but we want SCons to operate all
    # the way back to at least Python 1.5.2, which doesn't have it.
    h = string.hexdigits
    r = ''
    for c in s:
        try:
            i = ord(c)
        except:
            i = c
        r = r + h[(i >> 4) & 0xF] + h[i & 0xF]
    return r


def generateGUID(name):
    """This generates a dummy GUID for the sln file to use.  It is
    based on the MD5 signatures of the sln filename plus the name of
    the project.  It basically just needs to be unique, and not
    change with each invocation."""
    d = _hexdigest(hashlib.md5(str(name).encode()).digest()).upper()
    # convert most of the signature to GUID form (discard the rest)
    d = "{" + d[:8] + "-" + d[8:12] + "-" + d[12:16] + "-" + d[16:20] + "-" + d[20:32] + "}"
    return d


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


def path_from(path, base_node):
    if isinstance(path, str):
        return path
    else:
        return path.path_from(base_node)


def write_value(node, value, key=''):
    def convert_value(v):
        if isinstance(v, bool):
            return 'bool', v and 'true' or 'false'
        elif isinstance(v, float):
            return 'double', str(v)
        elif isinstance(v, int):
            return 'int', str(v)
        elif isinstance(v, bytearray):
            return 'QByteArray', str(v.decode('utf-8'))
        elif isinstance(v, str):
            return 'QString', str(v)
        elif isinstance(v, tuple):
            return 'QVariantList', ''
        elif isinstance(v, list):
            return 'QVariantMap', ''
        elif isinstance(v, datetime.datetime):
            return 'QDateTime', v.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            raise Exception('key \'%s\': unknown type in a map: %s' % (key, v.__class__.__name__))

    type, strvalue = convert_value(value)
    attrs = [('type', type)]
    if key:
        attrs.append(('key', key))
    if isinstance(value, tuple):
        with XmlNode(node, 'valuelist', strvalue, attrs) as value_list:
            for v in value:
                write_value(value_list, v)
    elif isinstance(value, list):
        with XmlNode(node, 'valuemap', strvalue, attrs) as value_map:
            for key, v in value:
                write_value(value_map, v, key)
    else:
        XmlNode(node, 'value', strvalue, attrs).close()


def read_value(node):
    type = node.attributes['type'].value
    if type == 'bool':
        if node.childNodes[0].wholeText == 'true':
            value = True
        else:
            value = False
    elif type == 'double':
        value = float(node.childNodes[0].wholeText)
    elif type == 'int':
        value = int(node.childNodes[0].wholeText)
    elif type == 'QByteArray':
        if node.childNodes:
            value = bytearray(node.childNodes[0].wholeText, 'utf-8')
        else:
            value = bytearray(b'')
    elif type == 'QString':
        if node.childNodes:
            value = node.childNodes[0].wholeText
        else:
            value = ''
    elif type == 'QVariantList':
        value = tuple((read_value(n)[1] for n in node.childNodes if n.nodeType == n.ELEMENT_NODE))
    elif type == 'QVariantMap':
        value = list([read_value(n) for n in node.childNodes if n.nodeType == n.ELEMENT_NODE])
    elif type == 'QDateTime':
        if node.childNodes:
            time = node.childNodes[0].wholeText.strip()
            if len(time) == 19:
                value = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
            elif len(time) == 23:
                value = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                raise ValueError('invalid date format: %s' % time)
        else:
            value = datetime.datetime(1970, 1, 1)
    else:
        Logs.warn('unknown Qt type: %s' % node.toxml())
        value = ''
    try:
        key = node.attributes['key'].value
    except Exception:
        key = ''
    return key, value


class QtObject:

    def load_from_node(self, xml_node):
        assert (xml_node.nodeName == 'valuemap')
        for node in xml_node.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                name, value = read_value(node)
                var_name = name.replace('.', '_')
                for n, u in self.__class__.published_vars:
                    if n == name:
                        break
                else:
                    self.__class__.published_vars.append((name, True))
                setattr(self, var_name, value)

    def copy_from(self, other):
        for (var_name, user_edit) in self.__class__.published_vars:
            if not user_edit:
                value = getattr(other, var_name.replace('.', '_'), None)
                if value:
                    setattr(self, var_name.replace('.', '_'), value)

    def write(self, xml_node):
        with XmlNode(xml_node, 'valuemap', [('type', 'QVariantMap')]) as variant_map:
            for (var_name, user_edit) in self.__class__.published_vars:
                value = getattr(self, var_name.replace('.', '_'), None)
                if value != None:
                    write_value(variant_map, value, key=var_name)


class QtCMakeTools(QtObject):
    published_vars = [
        ('AutoCreateBuildDirectory', False),
        ('AutoDetected', False),
        ('AutoRun', False),
        ('Binary', True),
        ('DetectionSource', True),
        ('DisplayName', True),
        ('Id', False),
        ('QchFile', True),
    ]


class QtToolchain(QtObject):
    published_vars = [
        ('ProjectExplorer.CustomToolChain.CompilerPath', False),
        ('ProjectExplorer.CustomToolChain.Cxx11Flags', True),
        ('ProjectExplorer.CustomToolChain.ErrorPattern', False),
        ('ProjectExplorer.CustomToolChain.FileNameCap', False),
        ('ProjectExplorer.CustomToolChain.HeaderPaths', False),
        ('ProjectExplorer.CustomToolChain.LineNumberCap', False),
        ('ProjectExplorer.CustomToolChain.MakePath', True),
        ('ProjectExplorer.CustomToolChain.MessageCap', False),
        ('ProjectExplorer.CustomToolChain.Mkspecs', False),
        ('ProjectExplorer.CustomToolChain.OutputParser', False),
        ('ProjectExplorer.CustomToolChain.PredefinedMacros', False),
        ('ProjectExplorer.GccToolChain.Path', False),
        ('ProjectExplorer.GccToolChain.TargetAbi', False),
        ('ProjectExplorer.GccToolChain.PlatformCodeGenFlags', False),
        ('ProjectExplorer.GccToolChain.PlatformLinkerFlags', False),
        ('ProjectExplorer.MsvcToolChain.VarsBat', False),
        ('ProjectExplorer.MsvcToolChain.VarsBatArg', False),
        ('ProjectExplorer.MsvcToolChain.SupportedAbi', False),
        ('ProjectExplorer.ToolChain.Language', False),
        ('ProjectExplorer.ToolChain.Autodetect', False),
        ('ProjectExplorer.ToolChain.DisplayName', True),
        ('ProjectExplorer.ToolChain.Id', False),
        ('Qt4ProjectManager.Android.NDK_TC_VERION', False),
    ]

    def get_architecture(self, env):
        return (env.ARCH_FAMILY, env.ARCH_LP64 and '64bit' or '32bit')

    def get_platform(self, env):
        target = env.COMPILER_TARGET
        supported_os = (
            ('linux', 'linux'),
            ('windows', 'windows'),
            ('mingw', 'windows'),
            ('freebsd', 'bsd'),
        )
        supported_platform = (
            ('android', 'android'),
            ('mingw', 'msys'),
            ('msvc 7.0', 'msvc2002'),
            ('msvc 7.1', 'msvc2003'),
            ('msvc 8.0', 'msvc2005'),
            ('msvc 9.0', 'msvc2008'),
            ('msvc 10.0', 'msvc2010'),
            ('msvc 11.0', 'msvc2012'),
            ('msvc 12.0', 'msvc2013'),
            ('msvc 14.0', 'msvc2015'),
            ('msvc 15.', 'msvc2017'),
            ('freebsd', 'freebsd'),
        )
        for o, o_name in supported_os:
            if target.find(o) != -1:
                os = o_name
                break
        else:
            os = 'unknown'
        for p, p_name in supported_platform:
            if target.find(p) != -1:
                platform = p_name
                break
        else:
            platform = 'unknown'
        return (os, platform)

    def __init__(self, language=None, env_name=None, env=None):
        if env_name:
            assert (env)
            arch, variant = self.get_architecture(env)
            os, platform = self.get_platform(env)
            abi = '%s-%s-%s-%s-%s' % (arch, os, platform, env.DEST_BINFMT, variant)
            compiler = env.CC if language == 1 else env.CXX
            original_flags = env.CFLAGS[:] if language == 1 else env.CXXFLAGS[:]
            flags = []
            while original_flags:
                f = original_flags.pop(0)
                if f == '-target':
                    f = original_flags.pop(0)
                    flags.append('--target=%s' % f)
            if isinstance(compiler, list):
                compiler = compiler[0]
            if compiler == 1:
                defines = env.COMPILER_C_DEFINES
                includes = env.COMPILER_C_INCLUDES
            else:
                defines = env.COMPILER_CXX_DEFINES
                includes = env.COMPILER_CXX_INCLUDES
            for define in env.DEFINES + defines:
                flags.append(env.DEFINES_ST % define)
            for include in env.INCLUDES + includes:
                flags.append(env.SYSTEM_INCLUDE_PATTERN % include)

            self.ProjectExplorer_CustomToolChain_CompilerPath = compiler
            self.ProjectExplorer_CustomToolChain_Cxx11Flags = ('-std=c++14')
            self.ProjectExplorer_CustomToolChain_ErrorPattern = ''
            self.ProjectExplorer_CustomToolChain_FileNameCap = 1
            self.ProjectExplorer_CustomToolChain_HeaderPaths = tuple(
                i.replace('\\', '/') for i in env.INCLUDES + includes
            )
            self.ProjectExplorer_CustomToolChain_LineNumberCap = 2
            self.ProjectExplorer_CustomToolChain_MakePath = ''
            self.ProjectExplorer_CustomToolChain_MessageCap = 3
            self.ProjectExplorer_CustomToolChain_Mkspecs = ''
            self.ProjectExplorer_CustomToolChain_OutputParser = 0
            toolchain_id = 'ProjectExplorer.ToolChain.Custom:%s' % generateGUID(
                'Motor:toolchain:%s:%d' % (env_name, language)
            )
            self.ProjectExplorer_CustomToolChain_PredefinedMacros = tuple(
                '#define %s' % ' '.join(d.split('=', 1)) for d in env.DEFINES + defines)
            self.ProjectExplorer_CustomToolChain_TargetAbi = abi
            self.ProjectExplorer_ToolChain_Language = language
            self.ProjectExplorer_ToolChain_Autodetect = False
            self.ProjectExplorer_ToolChain_DisplayName = 'Motor:toolchain:' + env_name
            self.ProjectExplorer_ToolChain_Id = toolchain_id


class QtDebugger(QtObject):
    published_vars = [
        ('Abis', False),
        ('AutoDetected', False),
        ('Binary', True),
        ('DisplayName', True),
        ('EngineType', True),
        ('Id', False),
        ('Debugger_Information', ''),
    ]

    def __init__(self, env_name=None, env=None, toolchain=None):
        if env_name:
            assert (env)
            assert (toolchain)
            if env.GDB:
                self.Binary = env.GDB[0]
                self.EngineType = 1
            elif env.CDB:
                self.Binary = env.CDB[0]
                self.EngineType = 4
            elif env.LLDB:
                self.Binary = env.LLDB[0]
                self.EngineType = 256
            else:
                self.Binary = '/usr/bin/gdb'
                self.EngineType = 1
            abi = getattr(toolchain, 'ProjectExplorer_CustomToolChain_TargetAbi', None)
            abi = abi or getattr(toolchain, 'ProjectExplorer_GccToolChain_TargetAbi', None)
            abi = abi or getattr(toolchain, 'ProjectExplorer_MsvcToolChain_TargetAbi', None)
            self.AutoDetected = False
            self.DisplayName = 'Motor:debugger:' + env_name
            self.Id = generateGUID('Motor:debugger:%s' % env_name)


class QtDevice(QtObject):

    def __init__(self):
        pass


class QtPlatform(QtObject):
    published_vars = [
        ('PE.Profile.AutoDetected', False),
        ('PE.Profile.Data', False),
        ('PE.Profile.Icon', True),
        ('PE.Profile.Id', False),
        ('PE.Profile.MutableInfo', True),
        ('PE.Profile.Name', True),
        ('PE.Profile.SDK', False),
    ]

    def __init__(self, bld, env_name=None, env=None, toolchain_c=None, toolchain_cxx=None, debugger=None, cmake=None):
        if env_name:
            assert (env)
            sysroot = env.SYSROOT or ''
            self.PE_Profile_AutoDetected = False
            if False and 'android' in env.VALID_PLATFORMS:
                device = 'Android Device'
                device_type = 'Android.Device.Type'
            else:
                device = 'Desktop Device'
                device_type = 'Desktop'
            self.PE_Profile_Data = [
                ('Debugger.Information', debugger),
                ('PE.Profile.Device', device),
                ('PE.Profile.DeviceType', device_type),
                ('PE.Profile.SysRoot', sysroot),
                ('PE.Profile.ToolChain', toolchain_c),
                ('PE.Profile.ToolChains', [('C', toolchain_c), ('Cxx', toolchain_cxx)]),
                ('PE.Profile.ToolChainsV3', [('C', toolchain_c), ('Cxx', toolchain_cxx)]),
                ('CMakeProjectManager.CMakeKitInformation', cmake),
                ('QtPM4.mkSPecInformation', ''),
                ('QtSupport.QtInformation', -1),
            ]
            icon_path = os.path.join(bld.motornode.abspath(), 'mak', 'res', '%s.png' % env.VALID_PLATFORMS[0])
            icon_extra = os.path.join(bld.motornode.abspath(), 'extra', env.VALID_PLATFORMS[0], 'icon.png')
            if os.path.isfile(icon_path):
                self.PE_Profile_Icon = icon_path
            elif os.path.isfile(icon_extra):
                self.PE_Profile_Icon = icon_extra
            else:
                self.PE_Profile_Icon = ':///Desktop///'
            self.PE_Profile_Id = self.guid = generateGUID('Motor:profile:' + env_name)
            self.PE_Profile_MutableInfo = ()
            self.PE_Profile_Name = 'Motor:profile:' + env_name
            self.PE_Profile_SDK = False


def to_var(name):
    return VAR_PATTERN % name


class QtCreator(Build.BuildContext):
    cmd = '_qtcreator'
    PROJECT_TYPE = 'GenericProjectManager.GenericBuildConfiguration'

    def execute(self):
        if self.schedule_setup():
            return "SKIP"

        self.restore()
        Options.options.nomaster = True
        if not self.all_envs:
            self.load_envs()
        self.variant = self.__class__.motor_variant
        self.env.PROJECTS = [self.__class__.cmd]
        self.env.VARIANT = to_var('Variant')
        self.env.TOOLCHAIN = to_var('Toolchain')
        self.env.PREFIX = to_var('Prefix')
        self.env.DEPLOY_ROOTDIR = to_var('Deploy_RootDir')
        self.env.DEPLOY_BINDIR = to_var('Deploy_BinDir')
        self.env.DEPLOY_RUNBINDIR = to_var('Deploy_RunBinDir')
        self.env.DEPLOY_LIBDIR = to_var('Deploy_LibDir')
        self.env.DEPLOY_INCLUDEDIR = to_var('Deploy_IncludeDir')
        self.env.DEPLOY_DATADIR = to_var('Deploy_DataDir')
        self.env.DEPLOY_PLUGINDIR = to_var('Deploy_PluginDir')
        self.env.DEPLOY_KERNELDIR = to_var('Deploy_KernelDir')
        self.features = ['GUI']
        self.recurse([self.run_dir])

        self.environment_id = self.get_environment_id()
        self.write_ini_file()
        self.build_platform_list()
        self.write_project_files()

    def write_ini_file(self):
        try:
            config_line = None
            max_index = None
            delete_index = None
            parse = False
            with open(INI_FILE, 'r') as ini_file:
                content = ini_file.readlines()
                for index, line in enumerate(content):
                    line = line.strip()
                    if line == '[ClangTools]':
                        config_line = index + 1
                        parse = True
                    elif line and line[0] == '[':
                        parse = False
                    if not parse:
                        continue
                    if line.startswith('ClangDiagnosticConfigs'):
                        config_line = index + 1
                        key, value = line.split('=')
                        key = key.split('\\')
                        if key[1] == 'size':
                            delete_index = index
                        else:
                            config_index = int(key[1])
                            if max_index is None or config_index > max_index:
                                max_index = config_index
                            if key[2] == 'id' and value == '{c75a31ba-e37d-4044-8825-36527d4ceea1}':
                                # found ClangTidy config, nothing to patch
                                return
            if delete_index is not None:
                del content[delete_index]
                if config_line > delete_index:
                    config_line -= 1
            if config_line is None:
                content += ['[ClangTools]\n', CLANG_TIDY_CONFIG.format(1), 'ClangDiagnosticConfigs\\size=1\n']
            elif max_index is None:
                content[config_line:config_line] = [CLANG_TIDY_CONFIG.format(1), 'ClangDiagnosticConfigs\\size=1\n']
            else:
                content[config_line:config_line] = [CLANG_TIDY_CONFIG.format(max_index+1), 'ClangDiagnosticConfigs\\size=%d\n'%(max_index+1)]

            with open(INI_FILE, 'w') as ini_file:
                ini_file.write(''.join(content))
        except IOError:
            print('QtCreator ini file not found; creating one')
            with open(INI_FILE, 'w') as ini_file:
                ini_file.write('[ClangTools]\n')
                ini_file.write(CLANG_TIDY_CONFIG.format(1))
                ini_file.write('ClangDiagnosticConfigs\\size=1\n')


    def write_project_files(self):
        appname = getattr(Context.g_module, Context.APPNAME, self.srcnode.name)
        self.base_node = self.srcnode.make_node('%s.qtcreator' % appname)
        self.base_node.mkdir()
        try:
            os.makedirs(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp'))
        except OSError:
            pass
        with open(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp', 'motor.xml'), 'w') as codestyle:
            self.write_codestyle(codestyle)

        projects = []
        for group in self.groups:
            for task_gen in group:
                if 'motor:kernel' in task_gen.features:
                    continue
                if 'motor:preprocess' in task_gen.features:
                    continue
                project_file = self.write_project(task_gen)
                projects.append(project_file)
                if task_gen == self.launcher:
                    launcher_project = project_file
                self.write_files(task_gen)
                includes, defines = self.gather_includes_defines(task_gen)
                self.write_includes(task_gen, includes)
                self.write_defines(task_gen, defines)
                node = self.base_node.make_node('%s.creator.user' % task_gen.target)
                with open(node.abspath(), 'w') as f:
                    self.write_user(f, [task_gen])
        self.write_workspace(projects, appname, launcher_project)

    def get_environment_id(self):
        try:
            with open(os.path.join(HOME_DIRECTORY, '..', 'QtCreator.ini')) as config:
                regexp = re.compile(r'Settings\\EnvironmentId=@ByteArray\((.*)\)$')
                for line in config.readlines():
                    result = regexp.match(line)
                    if result:
                        return bytearray(result.group(1), 'utf-8')
                else:
                    Logs.warn('QtCreator environment ID not found; creating dummy environment ID')
                    return bytearray(b'{9807fb0e-3785-4641-a197-bb1a10ccc985}')
        except IOError:
            Logs.warn('QtCreator config not found; creating dummy environment ID')
            return bytearray(b'{9807fb0e-3785-4641-a197-bb1a10ccc985}')

    def get_platform_guid(self, env_name):
        guid = generateGUID('Motor:profile:' + env_name)
        for platform_name, platform in self.platforms:
            if platform_name == guid:
                return guid

    def load_cmake_tools_list(self):
        self.cmake_tools = []
        self.cmake_tools_to_remove = []
        try:
            document = parse(os.path.join(HOME_DIRECTORY, 'cmaketools.xml'))
        except Exception as e:
            Logs.warn('QtCreator cmaketools not found; creating default one')
        else:
            for data in document.getElementsByTagName('data'):
                variable_name = data.getElementsByTagName('variable')[0]
                variable_name = variable_name.childNodes[0].toxml().strip()
                if variable_name.startswith('CMakeTools.'):
                    try:
                        variable_index = int(variable_name[11:])
                    except ValueError:
                        pass
                    else:
                        cmake_tools = QtCMakeTools()
                        cmake_tools.load_from_node(data.getElementsByTagName('valuemap')[0])
                        self.cmake_tools.append(cmake_tools)
                        if cmake_tools.DisplayName.startswith('Motor:'):
                            self.cmake_tools_to_remove.append(cmake_tools)
        if not self.cmake_tools:
            cmake = self.find_program('cmake', quiet=True, mandatory=False)
            if cmake:
                cmake_tool = QtCMakeTools()
                cmake_tool.Id = generateGUID('Motor:cmake')
                cmake_tool.AutoCreateBuildDirectory = False
                cmake_tool.AutoDetected = False
                cmake_tool.AutoRun = True
                cmake_tool.DetectionSource = ''
                cmake_tool.DisplayName = 'Motor:cmake'
                cmake_tool.QchFile = ''
                cmake_tool.Binary = cmake[0]
                self.cmake_tools.append(cmake_tool)

    def load_debugger_list(self):
        self.debuggers = []
        self.debuggers_to_remove = []
        try:
            document = parse(os.path.join(HOME_DIRECTORY, 'debuggers.xml'))
        except Exception as e:
            Logs.warn('QtCreator debuggers not found; creating default one')
        else:
            for data in document.getElementsByTagName('data'):
                variable_name = data.getElementsByTagName('variable')[0]
                variable_name = variable_name.childNodes[0].toxml().strip()
                if variable_name.startswith('DebuggerItem.'):
                    try:
                        variable_index = int(variable_name[13:])
                    except ValueError:
                        pass
                    else:
                        debugger = QtDebugger()
                        debugger.load_from_node(data.getElementsByTagName('valuemap')[0])
                        self.debuggers.append((debugger.Id, debugger))
                        if debugger.DisplayName.startswith('Motor:'):
                            self.debuggers_to_remove.append(debugger)

    def load_toolchain_list(self):
        self.toolchains = []
        self.toolchains_to_remove = []
        try:
            document = parse(os.path.join(HOME_DIRECTORY, 'toolchains.xml'))
        except Exception as e:
            Logs.warn('QtCreator toolchains not found; creating default one')
        else:
            for data in document.getElementsByTagName('data'):
                variable_name = data.getElementsByTagName('variable')[0]
                variable_name = variable_name.childNodes[0].toxml().strip()
                if variable_name.startswith('ToolChain.'):
                    try:
                        variable_index = int(variable_name[10:])
                    except ValueError:
                        pass
                    else:
                        toolchain = QtToolchain()
                        toolchain.load_from_node(data.getElementsByTagName('valuemap')[0])
                        self.toolchains.append((toolchain.ProjectExplorer_ToolChain_Id, toolchain))
                        if toolchain.ProjectExplorer_ToolChain_DisplayName.startswith('Motor:'):
                            self.toolchains_to_remove.append(toolchain)

    def load_device_list(self):
        self.devices = []
        try:
            document = parse(os.path.join(HOME_DIRECTORY, 'devices.xml'))
        except Exception as e:
            Logs.warn('QtCreator devices not found; creating default one')
        else:
            pass

    def load_platform_list(self):
        self.platforms = []
        self.platforms_to_remove = []
        try:
            document = parse(os.path.join(HOME_DIRECTORY, 'profiles.xml'))
        except Exception as e:
            Logs.warn('QtCreator profiles not found; creating default one')
        else:
            for data in document.getElementsByTagName('data'):
                variable_name = data.getElementsByTagName('variable')[0]
                variable_name = variable_name.childNodes[0].toxml().strip()
                if variable_name.startswith('Profile.'):
                    try:
                        variable_index = int(variable_name[8:])
                    except ValueError:
                        pass
                    else:
                        platform = QtPlatform(self, '')
                        platform.load_from_node(data.getElementsByTagName('valuemap')[0])
                        try:
                            platform.guid = platform.PE_Profile_Id
                        except AttributeError:
                            pass
                        else:
                            self.platforms.append((platform.PE_Profile_Id, platform))
                            if platform.PE_Profile_Name.startswith('Motor:'):
                                self.platforms_to_remove.append(platform)

    def build_platform_list(self):
        self.load_toolchain_list()
        if self.__class__.version[0] > 2:
            self.load_debugger_list()
        self.load_device_list()
        self.load_platform_list()
        self.load_cmake_tools_list()
        for env_name in self.env.ALL_TOOLCHAINS:
            env = self.all_envs[env_name]
            if env.SUB_TOOLCHAINS:
                bld_env = self.all_envs[env.SUB_TOOLCHAINS[0]]
            else:
                bld_env = env
            toolchains = [None, None]
            for l in (0, 1):
                toolchains[l] = QtToolchain(l + 1, env_name, bld_env)

                for t_name, t in self.toolchains:
                    if t_name == toolchains[l].ProjectExplorer_ToolChain_Id:
                        t.copy_from(toolchains[l])
                        toolchains[l] = t
                        try:
                            self.toolchains_to_remove.remove(t)
                        except ValueError:
                            pass
                        break
                else:
                    self.toolchains.append((toolchains[l].ProjectExplorer_ToolChain_Id, toolchains[l]))
            if self.__class__.version[0] == 2:
                if env.LLDB:
                    debugger = [
                        ('Binary', env.LLDB),
                        ('EngineType', 256),
                    ]
                elif env.CDB:
                    debugger = [
                        ('Binary', env.CDB),
                        ('EngineType', 4),
                    ]
                else:
                    debugger = [
                        ('Binary', env.GDB or '/usr/bin/gdb'),
                        ('EngineType', 1),
                    ]
            else:
                debugger = QtDebugger(env_name, env, toolchains[1])
                for d_name, d in self.debuggers:
                    if d_name == debugger.Id:
                        d.copy_from(debugger)
                        self.debuggers_to_remove.remove(d)
                        break
                else:
                    self.debuggers.append((debugger.Id, debugger))
                debugger = debugger.Id
            platform = QtPlatform(
                self, env_name, env, toolchains[0].ProjectExplorer_ToolChain_Id,
                toolchains[1].ProjectExplorer_ToolChain_Id, debugger, self.cmake_tools[0].Id
            )
            for p_name, p in self.platforms:
                if p_name == platform.PE_Profile_Id:
                    p.copy_from(platform)
                    self.platforms_to_remove.remove(p)
                    break
            else:
                self.platforms.append((platform.PE_Profile_Id, platform))

        if not os.path.exists(HOME_DIRECTORY):
            os.makedirs(HOME_DIRECTORY)
        with XmlDocument(
                open(os.path.join(HOME_DIRECTORY, 'profiles.xml'), 'w'), 'UTF-8', [('DOCTYPE', 'QtCreatorProfiles')]
        ) as document:
            with XmlNode(document, 'qtcreator') as creator:
                profile_index = 0
                for platform_name, platform in self.platforms:
                    if platform not in self.platforms_to_remove:
                        with XmlNode(creator, 'data') as data:
                            XmlNode(data, 'variable', 'Profile.%d' % profile_index)
                            platform.write(data)
                        profile_index += 1
                with XmlNode(creator, 'data') as data:
                    XmlNode(data, 'variable', 'Profile.Count')
                    XmlNode(data, 'value', str(profile_index), [('type', 'int')])
                with XmlNode(creator, 'data') as data:
                    XmlNode(data, 'variable', 'Profile.Default')
                    XmlNode(data, 'value', str(self.platforms[0][1].PE_Profile_Id), [('type', 'QString')])
                with XmlNode(creator, 'data') as data:
                    XmlNode(data, 'variable', 'Version')
                    XmlNode(data, 'value', '1', [('type', 'int')])

        with XmlDocument(
                open(os.path.join(HOME_DIRECTORY, 'debuggers.xml'), 'w'), 'UTF-8', [('DOCTYPE', 'QtCreatorDebugger')]
        ) as document:
            with XmlNode(document, 'qtcreator') as creator:
                debugger_index = 0
                for debugger_name, debugger in self.debuggers:
                    if debugger not in self.debuggers_to_remove:
                        with XmlNode(creator, 'data') as data:
                            XmlNode(data, 'variable', 'DebuggerItem.%d' % debugger_index)
                            debugger.write(data)
                        debugger_index += 1
                with XmlNode(creator, 'data') as data:
                    XmlNode(data, 'variable', 'DebuggerItem.Count')
                    XmlNode(data, 'value', str(debugger_index), [('type', 'int')])
                with XmlNode(creator, 'data') as data:
                    XmlNode(data, 'variable', 'Version')
                    XmlNode(data, 'value', '1', [('type', 'int')])

        with XmlDocument(
                open(os.path.join(HOME_DIRECTORY, 'cmaketools.xml'), 'w'), 'UTF-8', [('DOCTYPE', 'QtCreatorCMakeTools')]
        ) as document:
            with XmlNode(document, 'qtcreator') as creator:
                cmaketools_index = 0
                for cmaketools in self.cmake_tools:
                    if cmaketools not in self.cmake_tools_to_remove:
                        with XmlNode(creator, 'data') as data:
                            XmlNode(data, 'variable', 'CMakeTools.%d' % cmaketools_index)
                            cmaketools.write(data)
                        cmaketools_index += 1
                with XmlNode(creator, 'data') as data:
                    XmlNode(data, 'variable', 'CMakeTools.Count')
                    XmlNode(data, 'value', str(cmaketools_index), [('type', 'int')])
                if self.cmake_tools:
                    with XmlNode(creator, 'data') as data:
                        XmlNode(data, 'variable', 'CMakeTools.Default')
                        XmlNode(data, 'value', str(self.cmake_tools[0].Id), [('type', 'QString')])
                with XmlNode(creator, 'data') as data:
                    XmlNode(data, 'variable', 'Version')
                    XmlNode(data, 'value', '1', [('type', 'int')])

        with XmlDocument(
                open(os.path.join(HOME_DIRECTORY, 'toolchains.xml'), 'w'), 'UTF-8', [('DOCTYPE', 'QtCreatorToolChains')]
        ) as document:
            with XmlNode(document, 'qtcreator') as creator:
                toolchain_index = 0
                for toolchain_name, toolchain in self.toolchains:
                    if toolchain not in self.toolchains_to_remove:
                        with XmlNode(creator, 'data') as data:
                            XmlNode(data, 'variable', 'ToolChain.%d' % toolchain_index)
                            toolchain.write(data)
                        toolchain_index += 1
                with XmlNode(creator, 'data') as data:
                    XmlNode(data, 'variable', 'ToolChain.Count')
                    XmlNode(data, 'value', str(toolchain_index), [('type', 'int')])
                with XmlNode(creator, 'data') as data:
                    XmlNode(data, 'variable', 'Version')
                    XmlNode(data, 'value', '1', [('type', 'int')])

    def gather_includes_defines(self, task_gen):
        def gather_includes_defines_recursive(task_gen):
            try:
                return task_gen.bug_qtcreator_cache
            except AttributeError:
                includes = getattr(task_gen, 'export_includes', [])
                includes += getattr(task_gen, 'export_system_includes', [])
                defines = getattr(task_gen, 'export_defines', [])
                includes = [path_from(i, self.base_node) for i in includes]
                use = getattr(task_gen, 'use', [])
                for task_name in use:
                    try:
                        t = task_gen.bld.get_tgen_by_name(task_name)
                    except:
                        pass
                    else:
                        use_includes, use_defines = gather_includes_defines_recursive(t)
                        includes = includes + use_includes
                        defines = defines + use_defines
                task_gen.bug_qtcreator_cache = (includes, defines)
                return task_gen.bug_qtcreator_cache

        includes, defines = gather_includes_defines_recursive(task_gen)
        includes = includes + [path_from(i, self.base_node) for i in getattr(task_gen, 'includes', [])]
        defines = defines + getattr(task_gen, 'defines', [])
        return unique(includes), unique(defines)

    def write_codestyle(self, file):
        with XmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorCodeStyle')]) as cs:
            with XmlNode(cs, 'qtcreator') as qtcreator:
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'CodeStyleData').close()
                    write_value(
                        data, [
                            ("AlignAssignments", True),
                            ("AutoSpacesForTabs", False),
                            ("BindStarToIdentifier", False),
                            ("BindStarToLeftSpecifier", True),
                            ("BindStarToRightSpecifier", False),
                            ("BindStarToTypeName", True),
                            ("ExtraPaddingForConditionsIfConfusingAlign", False),
                            ("IndentAccessSpecifiers", False),
                            ("IndentBlockBody", True),
                            ("IndentBlockBraces", False),
                            ("IndentBlocksRelativeToSwitchLabels", True),
                            ("IndentClassBraces", False),
                            ("IndentControlFlowRelativeToSwitchLabels", True),
                            ("IndentDeclarationsRelativeToAccessSpecifiers", True),
                            ("IndentEnumBraces", False),
                            ("IndentFunctionBody", True),
                            ("IndentFunctionBraces", False),
                            ("IndentNamespaceBody", False),
                            ("IndentNamespaceBraces", False),
                            ("IndentSize", 4),
                            ("IndentStatementsRelativeToSwitchLabels", True),
                            ("IndentSwitchLabels", False),
                            ("PaddingMode", 2),
                            ("ShortGetterName", True),
                            ("SpacesForTabs", True),
                            ("TabSize", 4),
                        ]
                    )
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'DisplayName').close()
                    write_value(data, 'Motor')

    def write_codestyle(self, file):
        with XmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorCodeStyle')]) as cs:
            with XmlNode(cs, 'qtcreator') as qtcreator:
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'CodeStyleData').close()
                    write_value(
                        data, [
                            ("AlignAssignments", True),
                            ("AutoSpacesForTabs", False),
                            ("BindStarToIdentifier", False),
                            ("BindStarToLeftSpecifier", True),
                            ("BindStarToRightSpecifier", False),
                            ("BindStarToTypeName", True),
                            ("ExtraPaddingForConditionsIfConfusingAlign", False),
                            ("IndentAccessSpecifiers", False),
                            ("IndentBlockBody", True),
                            ("IndentBlockBraces", False),
                            ("IndentBlocksRelativeToSwitchLabels", True),
                            ("IndentClassBraces", False),
                            ("IndentControlFlowRelativeToSwitchLabels", True),
                            ("IndentDeclarationsRelativeToAccessSpecifiers", True),
                            ("IndentEnumBraces", False),
                            ("IndentFunctionBody", True),
                            ("IndentFunctionBraces", False),
                            ("IndentNamespaceBody", False),
                            ("IndentNamespaceBraces", False),
                            ("IndentSize", 4),
                            ("IndentStatementsRelativeToSwitchLabels", True),
                            ("IndentSwitchLabels", False),
                            ("PaddingMode", 2),
                            ("ShortGetterName", True),
                            ("SpacesForTabs", True),
                            ("TabSize", 4),
                        ]
                    )
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'DisplayName').close()
                    write_value(data, 'Motor')

    def write_project(self, task_gen):
        node = self.base_node.make_node('%s.creator' % task_gen.target)
        node.write('[General]')
        return node

    def write_files(self, task_gen):
        file_list = []
        for _, source_node in getattr(task_gen, 'source_nodes', []):
            try:
                file_list += [node.path_from(self.base_node) for node in source_node.ant_glob('**')]
            except Exception:
                pass
        self.base_node.make_node('%s.files' % task_gen.target).write('\n'.join(file_list))

    def write_includes(self, task_gen, includes):
        self.base_node.make_node('%s.includes' % task_gen.target).write('\n'.join(includes))

    def write_defines(self, task_gen, defines):
        self.base_node.make_node('%s.config' % task_gen.target).write('\n'.join(defines))

    def write_user(self, file, task_gens):
        with XmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorProject')]) as project:
            with XmlNode(project, 'qtcreator') as qtcreator:
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'EnvironmentId').close()
                    write_value(data, self.environment_id)
                with XmlNode(qtcreator, 'data') as data_node:
                    XmlNode(data_node, 'variable', 'ProjectExplorer.Project.ActiveTarget').close()
                    write_value(data_node, 0)
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'ProjectExplorer.Project.EditorSettings').close()
                    write_value(
                        data, [
                            ('EditorConfiguration.AutoIndent', True),
                            ('EditorConfiguration.AutoSpacesForTabs', False),
                            ('EditorConfiguration.CamelCaseNavigation', True),
                            (
                                'EditorConfiguration.CodeStyle.0', [
                                    ('language', 'Cpp'),
                                    ('value', [('CurrentPreferences', bytearray(b'motor'))]),
                                ]
                            ),
                            (
                                'EditorConfiguration.CodeStyle.1', [
                                    ('language', 'QmlJS'),
                                    ('value', [('CurrentPreferences', bytearray(b'QmlJSGlobal'))]),
                                ]
                            ),
                            ('EditorConfiguration.CodeStyle.Count', 2),
                            ('EditorConfiguration.Codec', bytearray(b'UTF-8')),
                            ('EditorConfiguration.ConstrainToolTips', False),
                            ('EditorConfiguration.IndentSize', 4),
                            ('EditorConfiguration.KeyboardTooltips', False),
                            ('EditorConfiguration.MarginColumn', 100),
                            ('EditorConfiguration.MouseNavigation', True),
                            ('EditorConfiguration.PaddingMode', 1),
                            ('EditorConfiguration.ScrollWheelZooming', True),
                            ('EditorConfiguration.ShowMargin', True),
                            ('EditorConfiguration.SmartBackspaceBehavior', 0),
                            ('EditorConfiguration.SpacesForTabs', True),
                            ('EditorConfiguration.TabKeyBehavior', 0),
                            ('EditorConfiguration.TabSize', 4),
                            ('EditorConfiguration.UseGlobal', False),
                            ('EditorConfiguration.Utf8BomBehavior', 1),
                            ('EditorConfiguration.addFinalNewLine', True),
                            ('EditorConfiguration.cleanIndentation', False),
                            ('EditorConfiguration.cleanWhitespace', True),
                            ('EditorConfiguration.inEntireDocument', False),
                        ]
                    )
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'ProjectExplorer.Project.PluginSettings').close()
                    write_value(data, [
                        ('ClangTools', [
                            ('ClangTools.AnalyzeOpenFiles', True),
                            ('ClangTools.BuildBeforeAnalysis', True),
                            ('ClangTools.DiagnosticConfig', '{c75a31ba-e37d-4044-8825-36527d4ceea1}'),
                            ('ClangTools.UseGlobalSettings', False)
                        ])
                    ])
                with XmlNode(qtcreator, 'data') as data:
                    target_index = 0
                    for env_name in self.env.ALL_TOOLCHAINS:
                        XmlNode(data, 'variable', 'ProjectExplorer.Project.Target.%d' % target_index).close()
                        bld_env = self.all_envs[env_name]
                        if bld_env.SUB_TOOLCHAINS:
                            env = self.all_envs[bld_env.SUB_TOOLCHAINS[0]]
                        else:
                            env = bld_env
                        build_configurations = []
                        deploy_configurations = []
                        build_configuration_index = 0
                        for variant in self.env.ALL_VARIANTS:
                            build_configurations.append(
                                self.make_build_configuration(build_configuration_index, bld_env, env, env_name,
                                                              variant))
                            build_configuration_index += 1
                        run_configurations = []
                        index = 0
                        for task_gen in task_gens:
                            if 'motor:game' in task_gen.features:
                                if 'android' in env.VALID_PLATFORMS:
                                    executable = env.ADB[0]
                                    arguments = 'shell am start com.motor/.MotorActivity --es %s' % task_gen.target
                                else:
                                    arguments = task_gen.target
                                    executable = to_var('OUT_NAME')
                                run_configurations.append(
                                    (
                                        'ProjectExplorer.Target.RunConfiguration.%d' % index, [
                                            ('Analyzer.Valgrind.AddedSuppressionFiles', ()),
                                            ('Analyzer.Valgrind.Callgrind.CollectBusEvents', False),
                                            ('Analyzer.Valgrind.Callgrind.CollectSystime', False),
                                            ('Analyzer.Valgrind.Callgrind.EnableBranchSim', False),
                                            ('Analyzer.Valgrind.Callgrind.EnableCacheSim', False),
                                            ('Analyzer.Valgrind.Callgrind.EnableEventTooltips', True),
                                            ('Analyzer.Valgrind.Callgrind.MinimumCastRatio', 0.01),
                                            ('Analyzer.Valgrind.Callgrind.VisualisationMinimumCostRatio', 10),
                                            ('Analyzer.Valgrind.FilterExternalIssues', True),
                                            ('Analyzer.Valgrind.LeakCheckOnFinish', 1),
                                            ('Analyzer.Valgrind.NumCallers', 32),
                                            ('Analyzer.Valgrind.RemovedSuppressionFiles', ()),
                                            ('Analyzer.Valgrind.SelfModifyingCodeDetection', 1),
                                            ('Analyzer.Valgrind.Settings.UseGlobalSettings', True),
                                            ('Analyzer.Valgrind.ShowReachable', False),
                                            ('Analyzer.Valgrind.TrackOrigins', True),
                                            ('Analyzer.Valgrind.ValgrindExecutable', 'valgrind'),
                                            (
                                                'Analyzer.Valgrind.VisibleErrorKinds',
                                                (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
                                            ),
                                            ('PE.EnvironmentAspect.Base', 2),
                                            ('PE.EnvironmentAspect.Changes', ()),
                                            ('ProjectExplorer.CustomExecutableRunConfiguration.Arguments', arguments),
                                            ('ProjectExplorer.CustomExecutableRunConfiguration.Executable', executable),
                                            ('ProjectExplorer.CustomExecutableRunConfiguration.UseTerminal', False),
                                            (
                                                'ProjectExplorer.CustomExecutableRunConfiguration.WorkingDirectory',
                                                to_var('OUT_DIR')
                                            ),
                                            (
                                                'ProjectExplorer.ProjectConfiguration.DefaultDisplayName',
                                                'Run %s' % task_gen.target
                                            ),
                                            (
                                                'ProjectExplorer.ProjectConfiguration.DisplayName',
                                                '%s:%s' % (self.launcher.target, task_gen.name)
                                            ),
                                            (
                                                'ProjectExplorer.ProjectConfiguration.Id',
                                                'ProjectExplorer.CustomExecutableRunConfiguration'
                                            ),
                                            ('RunConfiguration.QmlDebugServerPort', 3768),
                                            ('RunConfiguration.UseCppDebugger', True),
                                            ('RunConfiguration.UseCppDebuggerAuto', False),
                                            ('RunConfiguration.UseMultiProcess', False),
                                            ('RunConfiguration.UseQmlDebugger', False),
                                            ('RunConfiguration.UseQmlDebuggerAuto', True),
                                        ]
                                    )
                                )
                                index += 1
                            elif 'motor:python_module' in task_gen.features:
                                run_configurations.append(
                                    (
                                        'ProjectExplorer.Target.RunConfiguration.%d' % index, [
                                            ('Analyzer.Valgrind.AddedSuppressionFiles', ()),
                                            ('Analyzer.Valgrind.Callgrind.CollectBusEvents', False),
                                            ('Analyzer.Valgrind.Callgrind.CollectSystime', False),
                                            ('Analyzer.Valgrind.Callgrind.EnableBranchSim', False),
                                            ('Analyzer.Valgrind.Callgrind.EnableCacheSim', False),
                                            ('Analyzer.Valgrind.Callgrind.EnableEventTooltips', True),
                                            ('Analyzer.Valgrind.Callgrind.MinimumCastRatio', 0.01),
                                            ('Analyzer.Valgrind.Callgrind.VisualisationMinimumCostRatio', 10),
                                            ('Analyzer.Valgrind.FilterExternalIssues', True),
                                            ('Analyzer.Valgrind.LeakCheckOnFinish', 1),
                                            ('Analyzer.Valgrind.NumCallers', 32),
                                            ('Analyzer.Valgrind.RemovedSuppressionFiles', ()),
                                            ('Analyzer.Valgrind.SelfModifyingCodeDetection', 1),
                                            ('Analyzer.Valgrind.Settings.UseGlobalSettings', True),
                                            ('Analyzer.Valgrind.ShowReachable', False),
                                            ('Analyzer.Valgrind.TrackOrigins', True),
                                            ('Analyzer.Valgrind.ValgrindExecutable', 'valgrind'),
                                            (
                                                'Analyzer.Valgrind.VisibleErrorKinds',
                                                (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
                                            ),
                                            ('PE.EnvironmentAspect.Base', 2),
                                            ('PE.EnvironmentAspect.Changes', ()),
                                            (
                                                'ProjectExplorer.CustomExecutableRunConfiguration.Arguments',
                                                '-i -c "import %s"' % task_gen.target
                                            ),
                                            (
                                                'ProjectExplorer.CustomExecutableRunConfiguration.Executable',
                                                sys.executable
                                            ),
                                            ('ProjectExplorer.CustomExecutableRunConfiguration.UseTerminal', True),
                                            (
                                                'ProjectExplorer.CustomExecutableRunConfiguration.WorkingDirectory',
                                                to_var('RUNBIN_DIR')
                                            ),
                                            (
                                                'ProjectExplorer.ProjectConfiguration.DefaultDisplayName',
                                                'python:%s' % task_gen.target
                                            ),
                                            (
                                                'ProjectExplorer.ProjectConfiguration.DisplayName',
                                                'python:%s' % (task_gen.name)
                                            ),
                                            (
                                                'ProjectExplorer.ProjectConfiguration.Id',
                                                'ProjectExplorer.CustomExecutableRunConfiguration'
                                            ),
                                            ('RunConfiguration.QmlDebugServerPort', 3768),
                                            ('RunConfiguration.UseCppDebugger', True),
                                            ('RunConfiguration.UseCppDebuggerAuto', False),
                                            ('RunConfiguration.UseMultiProcess', False),
                                            ('RunConfiguration.UseQmlDebugger', False),
                                            ('RunConfiguration.UseQmlDebuggerAuto', True),
                                        ]
                                    )
                                )
                                index += 1

                        write_value(
                            data, [
                                      ('ProjectExplorer.ProjectConfiguration.DefaultDisplayName', env_name),
                                      ('ProjectExplorer.ProjectConfiguration.DisplayName', env_name),
                                      ('ProjectExplorer.ProjectConfiguration.Id', self.get_platform_guid(env_name)),
                                      ('ProjectExplorer.Target.ActiveBuildConfiguration', 0),
                                      ('ProjectExplorer.Target.ActiveDeployConfiguration', 0),
                                      ('ProjectExplorer.Target.ActiveRunConfiguration', 0),
                                  ] + build_configurations + [
                                      ('ProjectExplorer.Target.BuildConfigurationCount', len(build_configurations)),
                                      ('ProjectExplorer.Target.DeployConfigurationCount', 0),
                                      ('ProjectExplorer.Target.PluginSettings', [])
                                  ] + run_configurations + [
                                      ('ProjectExplorer.Target.RunConfigurationCount', len(run_configurations)),
                                  ]
                        )
                        target_index += 1
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'ProjectExplorer.Project.TargetCount').close()
                    write_value(data, target_index)
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'ProjectExplorer.Project.Updater.FileVersion').close()
                    write_value(data, self.__class__.version[1])
                with XmlNode(qtcreator, 'data') as data:
                    XmlNode(data, 'variable', 'Version').close()
                    write_value(data, self.__class__.version[1])

    def make_build_configuration(self, build_configuration_index, bld_env, env, env_name, variant):
        options = [a for a in sys.argv if a[0] == '-']
        target_os = qbsPlatformList(env)
        extraPlatformFlags = target_os and [
            ('qbs.targetOS', target_os),
        ] or []
        return (
            'ProjectExplorer.Target.BuildConfiguration.%d' % build_configuration_index, [
                (
                    'ProjectExplorer.BuildConfiguration.BuildDirectory',
                    self.bldnode.make_node('qtcreator').abspath()
                ),
                (
                    'GenericProjectManager.GenericBuildConfiguration.BuildDirectory',
                    self.bldnode.make_node('qtcreator').abspath()
                ),
                (
                    'ProjectExplorer.BuildConfiguration.BuildStepList.0', [
                        (
                            'ProjectExplorer.BuildStepList.Step.0', [
                                ('ProjectExplorer.BuildStep.Enabled', False),
                                (
                                    'ProjectExplorer.ProjectConfiguration.DefaultDisplayName',
                                    'Qbs configuration'
                                ), ('ProjectExplorer.ProjectConfiguration.DisplayName', ''),
                                (
                                    'Qbs.Configuration', [
                                        ('qbs.buildVariant', variant),
                                        ('qbs.architecture', qbsArch(env.TARGET_ARCH)),
                                        ('qbs.targetPlatform', qbsPlatform(env)),
                                    ] + extraPlatformFlags
                                ), ('ProjectExplorer.ProjectConfiguration.Id', 'Qbs.BuildStep')
                            ]
                        ),
                        (
                            'ProjectExplorer.BuildStepList.Step.1', [
                                ('ProjectExplorer.BuildStep.Enabled', True),
                                (
                                    'ProjectExplorer.ProcessStep.Arguments',
                                    '%s build:%s:%s %s' %
                                    (sys.argv[0], env_name, variant, ' '.join(options))
                                ),
                                ('ProjectExplorer.ProcessStep.Command', sys.executable),
                                (
                                    'ProjectExplorer.ProcessStep.WorkingDirectory',
                                    self.srcnode.abspath()
                                ),
                                (
                                    'ProjectExplorer.ProjectConfiguration.DefaultDisplayName',
                                    'Waf configuration'
                                ),
                                ('ProjectExplorer.ProjectConfiguration.DisplayName', ''),
                                (
                                    'ProjectExplorer.ProjectConfiguration.Id',
                                    'ProjectExplorer.ProcessStep'
                                ),
                            ]
                        ), ('ProjectExplorer.BuildStepList.StepsCount', 2),
                        ('ProjectExplorer.ProjectConfiguration.DefaultDisplayName', 'Build'),
                        ('ProjectExplorer.ProjectConfiguration.DisplayName', ''),
                        (
                            'ProjectExplorer.ProjectConfiguration.Id',
                            'ProjectExplorer.BuildSteps.Build'
                        )
                    ]
                ),
                (
                    'ProjectExplorer.BuildConfiguration.BuildStepList.1', [
                        (
                            'ProjectExplorer.BuildStepList.Step.0', [
                                ('ProjectExplorer.BuildStep.Enabled', True),
                                (
                                    'ProjectExplorer.ProcessStep.Arguments',
                                    '%s clean:%s:%s' % (sys.argv[0], env_name, variant)
                                ), ('ProjectExplorer.ProcessStep.Command', sys.executable),
                                (
                                    'ProjectExplorer.ProcessStep.WorkingDirectory',
                                    self.srcnode.abspath()
                                ),
                                (
                                    'ProjectExplorer.ProjectConfiguration.DefaultDisplayName',
                                    'Waf configuration'
                                ), ('ProjectExplorer.ProjectConfiguration.DisplayName', ''),
                                (
                                    'ProjectExplorer.ProjectConfiguration.Id',
                                    'ProjectExplorer.ProcessStep'
                                )
                            ]
                        ), ('ProjectExplorer.BuildStepList.StepsCount', 1),
                        ('ProjectExplorer.ProjectConfiguration.DefaultDisplayName', 'Clean'),
                        ('ProjectExplorer.ProjectConfiguration.DisplayName', ''),
                        (
                            'ProjectExplorer.ProjectConfiguration.Id',
                            'ProjectExplorer.BuildSteps.Clean'
                        )
                    ]
                ), ('ProjectExplorer.BuildConfiguration.BuildStepListCount', 2),
                ('ProjectExplorer.BuildConfiguration.ClearSystemEnvironment', False),
                (
                    'ProjectExplorer.BuildConfiguration.UserEnvironmentChanges',
                    tuple(
                        '%s=%s' % (var_name, bld_env[var_name.upper()]) for var_name in (
                            'Toolchain', 'Prefix', 'Deploy_RootDir', 'Deploy_BinDir',
                            'Deploy_RunBinDir', 'Deploy_LibDir', 'Deploy_IncludeDir',
                            'Deploy_DataDir'
                        )
                    ) + (
                        'OUT_NAME=%s' % os.path.join(
                            self.srcnode.abspath(), bld_env.PREFIX, variant, env.DEPLOY_BINDIR,
                            env.cxxprogram_PATTERN % self.launcher.target
                        ), 'OUT_DIR=%s' %
                        os.path.join(self.srcnode.abspath(), bld_env.PREFIX, variant),
                        'RUNBIN_DIR=%s' % os.path.join(
                            self.srcnode.abspath(), bld_env.PREFIX, variant,
                            env.DEPLOY_RUNBINDIR
                        ), 'TERM=msys', 'Python="%s"' % sys.executable,
                        'SrcDir="%s"' % self.srcnode.abspath(), 'Variant=%s' % variant,
                        'PATH=%s' % os.environ['PATH']
                    )
                ), ('ProjectExplorer.ProjectConfiguration.DefaultDisplayName', 'Default'),
                ('ProjectExplorer.ProjectConfiguration.DisplayName', variant),
                ('ProjectExplorer.ProjectConfiguration.Id', self.PROJECT_TYPE)
            ]
        )

    def write_workspace(self, projects, appname, launcher):
        workspace_file = os.path.join(HOME_DIRECTORY, '%s.qws' % appname)
        try:
            document = parse(workspace_file)
        except Exception:
            with XmlDocument(open(workspace_file, 'w'), 'UTF-8', [('DOCTYPE', 'QtCreatorSession')]) as document:
                with XmlNode(document, 'qtcreator') as creator:
                    with XmlNode(creator, 'data') as data:
                        XmlNode(data, 'variable', 'Color').close()
                        XmlNode(data, 'value', '#666666', {'type': 'QString'}).close()
                    with XmlNode(creator, 'data') as data:
                        XmlNode(data, 'variable', 'EditorSettings').close()
                        XmlNode(data, 'value', '', {'type': 'QByteArray'}).close()
                    with XmlNode(creator, 'data') as data:
                        XmlNode(data, 'variable', 'ProjectDependencies').close()
                        XmlNode(data, 'valuemap', '', {'type': 'QVariantMap'}).close()
                    with XmlNode(creator, 'data') as data:
                        XmlNode(data, 'variable', 'ProjectList').close()
                        with XmlNode(data, 'valuelist', '', {'type': 'QVariantList'}) as project_list:
                            for project in projects:
                                XmlNode(project_list, 'value', project.abspath(), {'type': 'QString'}).close()
                    with XmlNode(creator, 'data') as data:
                        XmlNode(data, 'variable', 'StartupProject').close()
                        XmlNode(data, 'value', launcher.abspath(), {'type': 'QString'}).close()
                    with XmlNode(creator, 'data') as data:
                        XmlNode(data, 'variable', 'valueKeys').close()
                        XmlNode(data, 'valuelist', '', {'type': 'QVariantList'}).close()
        else:
            new_valuelist = document.createElement('valuelist')
            new_valuelist.setAttribute('type', 'QVariantList')
            for project in projects:
                new_valuelist.appendChild(document.createTextNode('\n   '))
                project_node = document.createElement('value')
                project_node.setAttribute('type', 'QString')
                project_name = document.createTextNode(project.abspath().replace('\\', '/'))
                project_node.appendChild(project_name)
                new_valuelist.appendChild(project_node)
            new_valuelist.appendChild(document.createTextNode('\n  '))

            for element in document.getElementsByTagName('variable'):
                if element.firstChild.nodeType == element.firstChild.TEXT_NODE and element.firstChild.data == 'ProjectList':
                    data = element.parentNode
                    old_valuelist = data.getElementsByTagName('valuelist')[0]
                    data.replaceChild(new_valuelist, old_valuelist)
            with open(workspace_file, 'w') as new_file:
                new_file.write(document.toxml())


class Qbs(QtCreator):
    cmd = '_qbs'
    PROJECT_TYPE = 'Qbs.QbsBuildConfiguration'

    def write_project_files(self):
        appname = getattr(Context.g_module, Context.APPNAME, self.srcnode.name)
        self.base_node = self.srcnode
        qbs_project = self.base_node.make_node('%s.qbs' % appname)
        qbs_user = self.base_node.make_node('%s.qbs.user' % appname)
        try:
            os.makedirs(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp'))
        except OSError:
            pass
        with open(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp', 'motor.xml'), 'w') as codestyle:
            self.write_codestyle(codestyle)
        projects = {}
        project_list = []
        for group in self.groups:
            for task_gen in group:
                if 'motor:kernel' in task_gen.features:
                    continue
                if 'motor:preprocess' in task_gen.features:
                    continue
                task_gen.post()
                try:
                    name = task_gen.module_path.split('.')
                except AttributeError:
                    name = task_gen.name.split('.')
                p = projects
                for c in name[:-1]:
                    try:
                        p = p[c]
                    except KeyError:
                        p[c] = {}
                        p = p[c]
                p[name[-1]] = task_gen
                project_list.append(task_gen)
        with open(qbs_project.abspath(), 'w') as pfile:
            pfile.write('import qbs\n\n')
            pfile.write('Project {\n')
            pfile.write('    name: "%s"\n' % appname)
            self.write_project_list(pfile, projects)
            pfile.write('}\n')
        with open(qbs_user.abspath(), 'w') as f:
            self.write_user(f, project_list)

    def write_project_list(self, project_file, project_list, indent='    '):
        for k in sorted(project_list.keys()):
            p = project_list[k]
            if isinstance(p, dict):
                project_file.write('%sProject {\n' % indent)
                project_file.write('%s    name: "%s"\n' % (indent, k))
                self.write_project_list(project_file, p, indent + '    ')
                project_file.write('%s}\n' % indent)
            else:
                includes, defines = self.gather_includes_defines(p)
                project_file.write('%sProduct {\n' % indent)
                project_file.write('%s    Depends { name: "cpp" }\n' % (indent))
                for env_name in self.env.ALL_TOOLCHAINS:
                    env = self.all_envs[env_name]
                    if env.SUB_TOOLCHAINS:
                        env = self.all_envs[env.SUB_TOOLCHAINS[0]]
                    if 'android' in env.VALID_PLATFORMS:
                        ndk_root = env.ANDROID_NDK_PATH
                        host_name = os.path.split(os.path.dirname(os.path.dirname(env.CC[0])))[1]
                        project_file.write('%s    Depends { name: "Android.ndk" }\n' % indent)
                        project_file.write('%s    Depends { name: "codesign" }\n' % indent)
                        project_file.write('%s    Android.ndk.hostArch: "%s"\n' % (indent, host_name))
                        project_file.write('%s    Android.ndk.ndkDir: "%s"\n' % (indent, ndk_root))
                        project_file.write('%s    codesign.debugKeystorePath: "%s"\n' % (indent, env.ANDROID_DEBUGKEY))
                        break

                project_file.write('%s    name: "%s"\n' % (indent, p.name))
                project_file.write('%s    targetName: "%s"\n' % (indent, p.name.split('.')[-1]))
                project_file.write('%s    cpp._skipAllChecks: true\n' % (indent,))
                project_file.write('%s    cpp.includePaths: [\n' % (indent))
                for include in includes:
                    project_file.write('%s        "%s",\n' % (indent, include.replace('\\', '/')))
                project_file.write('%s    ]\n' % (indent))
                project_file.write('%s    cpp.defines: [\n' % (indent))
                for define in defines:
                    project_file.write('%s        "%s",\n' % (indent, define))
                project_file.write('%s    ]\n' % (indent))
                project_file.write('%s    files: [\n' % indent)
                for _, source_node in getattr(p, 'source_nodes', []):
                    if source_node.isdir():
                        for node in source_node.ant_glob('**'):
                            for r in IGNORE_PATTERNS:
                                if r.match(node.abspath()):
                                    break
                            else:
                                node_path = node.path_from(self.srcnode).replace('\\', '/')
                                project_file.write('%s        "%s",\n' % (indent, node_path))
                    else:
                        node_path = source_node.path_from(self.srcnode).replace('\\', '/')
                        project_file.write('%s        "%s",\n' % (indent, node_path))
                project_file.write('%s    ]\n' % indent)
                project_file.write('%s}\n' % indent)


class QCMake(QtCreator):
    cmd = 'qcmake'
    PROJECT_TYPE = 'CMakeProjectManager.CMakeBuildConfiguration'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/qcmake'
    version = (4, 18)

    def write_project_files(self):
        self.cmake_toolchains = {}
        for env_name, toolchain in cmake.write_cmake_workspace(self):
            self.cmake_toolchains[env_name] = toolchain
        appname = getattr(Context.g_module, Context.APPNAME, self.srcnode.name)
        self.base_node = self.srcnode
        cmake_user = self.base_node.make_node('CMakeLists.txt.user')
        try:
            os.makedirs(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp'))
        except OSError:
            pass
        with open(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp', 'motor.xml'), 'w') as codestyle:
            self.write_codestyle(codestyle)
        project_list = []
        for group in self.groups:
            for task_gen in group:
                if 'motor:kernel' in task_gen.features:
                    continue
                if 'motor:preprocess' in task_gen.features:
                    continue
                project_list.append(task_gen)
        with open(cmake_user.abspath(), 'w') as f:
            self.write_user(f, project_list)

    def make_build_configuration(self, build_configuration_index, bld_env, env, env_name, variant):
        return (
            'ProjectExplorer.Target.BuildConfiguration.%d' % build_configuration_index, [
                ('CMake.Build.Type', variant),
                ('CMake.Configure.ClearSystemEnvironment', False),
                ('CMake.Configure.UserEnvironmentChanges', tuple()),
                ('CMake.Initial.Parameters',
                 '-DCMAKE_BUILD_TYPE:STRING=%s\n'
                 '-DCMAKE_TOOLCHAIN_FILE:STRING=%s\n'
                 '-DCMAKE_C_COMPILER:FILEPATH=%%{Compiler:Executable:C}\n'
                 '-DCMAKE_CXX_COMPILER:FILEPATH=%%{Compiler:Executable:Cxx}' % (
                     variant, self.cmake_toolchains[env_name])),
                (
                    'ProjectExplorer.BuildConfiguration.BuildDirectory',
                    self.bldnode.make_node('%s/%s' % (env_name, variant)).abspath()
                ),
                (
                    'GenericProjectManager.GenericBuildConfiguration.BuildDirectory',
                    self.bldnode.make_node('%s/%s' % (env_name, variant)).abspath()
                ),
                (
                    'ProjectExplorer.BuildConfiguration.BuildStepList.0', [
                        (
                            'ProjectExplorer.BuildStepList.Step.0', [
                                ('CMakeProjectManager.MakeStep.BuildPreset', ''),
                                ('CMakeProjectManager.MakeStep.BuildTargets', ('all',)),
                                ('CMakeProjectManager.MakeStep.ClearSystemEnvironment', False),
                                ('CMakeProjectManager.MakeStep.UserEnvironmentChanges', tuple()),
                                ('ProjectExplorer.BuildStep.Enabled', True),
                                ('ProjectExplorer.ProjectConfiguration.DisplayName', 'Build'),
                                ('ProjectExplorer.ProjectConfiguration.Id', 'CMakeProjectManager.MakeStep')
                            ]
                        ),
                        ('ProjectExplorer.BuildStepList.StepsCount', 1),
                        ('ProjectExplorer.ProjectConfiguration.DefaultDisplayName', 'Build'),
                        ('ProjectExplorer.ProjectConfiguration.DisplayName', 'Build'),
                        (
                            'ProjectExplorer.ProjectConfiguration.Id',
                            'ProjectExplorer.BuildSteps.Build'
                        )
                    ]
                ),
                (
                    'ProjectExplorer.BuildConfiguration.BuildStepList.1', [
                        (
                            'ProjectExplorer.BuildStepList.Step.0', [
                                ('CMakeProjectManager.MakeStep.BuildPreset', ''),
                                ('CMakeProjectManager.MakeStep.BuildTargets', ('clean',)),
                                ('CMakeProjectManager.MakeStep.ClearSystemEnvironment', False),
                                ('CMakeProjectManager.MakeStep.UserEnvironmentChanges', tuple()),
                                ('ProjectExplorer.BuildStep.Enabled', True),
                                ('ProjectExplorer.ProjectConfiguration.DisplayName', 'Clean'),
                                ('ProjectExplorer.ProjectConfiguration.Id', 'CMakeProjectManager.MakeStep')
                            ]
                        ),
                        (
                            'ProjectExplorer.BuildStepList.Step.1', [
                                ('ProjectExplorer.BuildStep.Enabled', True),
                                (
                                    'ProjectExplorer.ProcessStep.Arguments',
                                    '%s clean:%s:%s' % (sys.argv[0], env_name, variant)
                                ),
                                ('ProjectExplorer.ProcessStep.Command', sys.executable),
                                (
                                    'ProjectExplorer.ProcessStep.WorkingDirectory',
                                    self.srcnode.abspath()
                                ),
                                (
                                    'ProjectExplorer.ProjectConfiguration.DefaultDisplayName',
                                    'Waf configuration'
                                ),
                                ('ProjectExplorer.ProjectConfiguration.DisplayName', ''),
                                ('ProjectExplorer.ProjectConfiguration.Id', 'ProjectExplorer.ProcessStep')
                            ]
                        ),
                        ('ProjectExplorer.BuildStepList.StepsCount', 2),
                        ('ProjectExplorer.ProjectConfiguration.DefaultDisplayName', 'Clean'),
                        ('ProjectExplorer.ProjectConfiguration.DisplayName', ''),
                        (
                            'ProjectExplorer.ProjectConfiguration.Id',
                            'ProjectExplorer.BuildSteps.Clean'
                        )
                    ]
                ),
                ('ProjectExplorer.BuildConfiguration.BuildStepListCount', 2),
                ('ProjectExplorer.BuildConfiguration.ClearSystemEnvironment', False),
                (
                    'ProjectExplorer.BuildConfiguration.UserEnvironmentChanges',
                    tuple(
                        '%s=%s' % (var_name, bld_env[var_name.upper()]) for var_name in (
                            'Toolchain', 'Prefix', 'Deploy_RootDir', 'Deploy_BinDir',
                            'Deploy_RunBinDir', 'Deploy_LibDir', 'Deploy_IncludeDir',
                            'Deploy_DataDir'
                        )
                    ) + (
                        'OUT_NAME=%s' % os.path.join(
                            self.srcnode.abspath(), bld_env.PREFIX, variant, env.DEPLOY_BINDIR,
                            env.cxxprogram_PATTERN % self.launcher.target
                        ), 'OUT_DIR=%s' %
                        os.path.join(self.srcnode.abspath(), bld_env.PREFIX, variant),
                        'RUNBIN_DIR=%s' % os.path.join(
                            self.srcnode.abspath(), bld_env.PREFIX, variant,
                            env.DEPLOY_RUNBINDIR
                        ), 'TERM=msys', 'Python="%s"' % sys.executable,
                        'SrcDir="%s"' % self.srcnode.abspath(), 'Variant=%s' % variant,
                        'PATH=%s' % os.environ['PATH']
                    )
                ), ('ProjectExplorer.ProjectConfiguration.DefaultDisplayName', 'Default'),
                ('ProjectExplorer.ProjectConfiguration.DisplayName', variant),
                ('ProjectExplorer.ProjectConfiguration.Id', self.PROJECT_TYPE)
            ]
        )


class QtCreator2(QtCreator):
    "creates projects for QtCreator 2.x"
    cmd = 'qtcreator2'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/qtcreator2'
    version = (2, 12)


class QtCreator3(QtCreator):
    "creates projects for QtCreator 3.x"
    cmd = 'qtcreator3'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/qtcreator3'
    version = (3, 15)


class QtCreator4(QtCreator):
    "creates projects for QtCreator 4.x"
    cmd = 'qtcreator4'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/qtcreator4'
    version = (4, 18)


class Qbs2(Qbs):
    "creates Qbs projects for QtCreator 2.x"
    cmd = 'qbs2'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/qbs2'
    version = (2, 12)


class Qbs3(Qbs):
    "creates Qbs projects for QtCreator 3.x"
    cmd = 'qbs3'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/qbs3'
    version = (3, 15)


class Qbs4(Qbs):
    "creates Qbs projects for QtCreator 4.x"
    cmd = 'qbs4'
    fun = 'build'
    optim = 'debug'
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/qbs4'
    version = (4, 18)
