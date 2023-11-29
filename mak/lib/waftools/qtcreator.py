#! /Usr/bin/env python
# ! /Usr/bin/env python
# encoding: utf-8

import os
import sys
import re
import datetime

import build_framework
import waflib.ConfigSet
import waflib.Configure
import waflib.Context
import waflib.Logs
import waflib.Node
import waflib.Options
import waflib.TaskGen
import waftools_common.minixml
import waftools_common.utils
import waftools_common.cmake
import xml.dom.minidom
from typing import Any, Dict, IO, List, Optional, Tuple, Union

if sys.platform == 'win32':
    HOME_DIRECTORY = os.path.join(os.getenv('APPDATA'), 'QtProject', 'qtcreator')
    INI_FILE = os.path.join(os.getenv('APPDATA'), 'QtProject', 'QtCreator.ini')
else:
    HOME_DIRECTORY = os.path.join(os.path.expanduser('~'), '.config', 'QtProject', 'qtcreator')
    INI_FILE = os.path.join(os.path.expanduser('~'), '.config', 'QtProject', 'QtCreator.ini')

VAR_PATTERN = '${%s}' if sys.platform != 'win32' else '%%%s%%'

IGNORE_PATTERNS = [
    re.compile(r'.*\.pyc'),
    re.compile(r'.*__pycache__.*'),
]

CLANG_TIDY_CONFIG = "ClangDiagnosticConfigs\\{0}\\clangTidyChecks=\n" \
                    "ClangDiagnosticConfigs\\{0}\\clangTidyChecksOptions=@Variant(\\0\\0\\0\\b\\0\\0\\0\\0)\n" \
                    "ClangDiagnosticConfigs\\{0}\\clangTidyMode=2\n" \
                    "ClangDiagnosticConfigs\\{0}\\clazyChecks=\n" \
                    "ClangDiagnosticConfigs\\{0}\\clazyMode=0\n" \
                    "ClangDiagnosticConfigs\\{0}\\diagnosticOptions=-w\n" \
                    "ClangDiagnosticConfigs\\{0}\\displayName=Motor\n" \
                    "ClangDiagnosticConfigs\\{0}\\id={{c75a31ba-e37d-4044-8825-36527d4ceea1}}\n" \
                    "ClangDiagnosticConfigs\\{0}\\useBuildSystemFlags=false\n"


def _qbs_arch(arch_name: str) -> str:
    archs = {'amd64': 'x86_64', 'x64': 'x86_64', 'x86_amd64': 'x86_64', 'aarch64': 'arm64'}
    return archs.get(arch_name, arch_name)


def _qbs_platform(env: waflib.ConfigSet.ConfigSet) -> str:
    if 'iphonesimulator' in env.VALID_PLATFORMS:
        return 'ios-simulator'
    elif 'iphone' in env.VALID_PLATFORMS:
        return 'ios'
    else:
        return env.VALID_PLATFORMS[0]


def _qbs_platform_list(env: waflib.ConfigSet.ConfigSet) -> Optional[str]:
    if 'iphonesimulator' in env.VALID_PLATFORMS:
        return '["ios-simulator","ios","darwin","bsd","unix"]'
    elif 'iphone' in env.VALID_PLATFORMS:
        return '["ios","darwin","bsd","unix"]'
    else:
        return None


def _convert_value(key: str, v: Any) -> Tuple[str, str]:
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


def _write_value(node: waftools_common.minixml.XmlNode, value: Any, key: str = '') -> None:
    value_type, strvalue = _convert_value(key, value)
    attrs = [('type', value_type)]
    if key:
        attrs.append(('key', key))
    if isinstance(value, tuple):
        with waftools_common.minixml.XmlNode(node, 'valuelist', strvalue, attrs) as value_list:
            for v in value:
                _write_value(value_list, v)
    elif isinstance(value, list):
        with waftools_common.minixml.XmlNode(node, 'valuemap', strvalue, attrs) as value_map:
            for key, v in value:
                _write_value(value_map, v, key)
    else:
        waftools_common.minixml.XmlNode(node, 'value', strvalue, attrs).close()


def _read_value(node: xml.dom.minidom.Element) -> Tuple[str, Any]:
    try:
        key = node.attributes['key'].value
    except KeyError:
        key = ''
    node_type = node.attributes['type'].value

    if node_type == 'bool':
        if node.childNodes[0].wholeText == 'true':
            return key, True
        else:
            return key, False
    elif node_type == 'double':
        return key, float(node.childNodes[0].wholeText)
    elif node_type == 'int':
        return key, int(node.childNodes[0].wholeText)
    elif node_type == 'QByteArray':
        if node.childNodes:
            return key, bytearray(node.childNodes[0].wholeText, 'utf-8')
        else:
            return key, bytearray(b'')
    elif node_type == 'QString':
        if node.childNodes:
            return key, node.childNodes[0].wholeText
        else:
            return key, ''
    elif node_type == 'QVariantList':
        return key, tuple((_read_value(n)[1] for n in node.childNodes if n.nodeType == n.ELEMENT_NODE))
    elif node_type == 'QVariantMap':
        return key, list([_read_value(n) for n in node.childNodes if n.nodeType == n.ELEMENT_NODE])
    elif node_type == 'QDateTime':
        if node.childNodes:
            time = node.childNodes[0].wholeText.strip()
            if len(time) == 19:
                return key, datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
            elif len(time) == 23:
                return key, datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                raise ValueError('invalid date format: %s' % time)
        else:
            return key, datetime.datetime(1970, 1, 1)
    else:
        waflib.Logs.warn('unknown Qt type: %s' % node.toxml())
        return key, ''


class QtObject:
    published_vars = []  # type: List[Tuple[str, bool]]

    def load_from_node(self, xml_node: xml.dom.minidom.Element) -> None:
        assert (xml_node.nodeName == 'valuemap')
        for node in xml_node.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                name, value = _read_value(node)
                var_name = name.replace('.', '_')
                for n, u in self.__class__.published_vars:
                    if n == name:
                        break
                else:
                    self.__class__.published_vars.append((name, True))
                setattr(self, var_name, value)

    def copy_from(self, other: "QtObject") -> None:
        for (var_name, user_edit) in self.__class__.published_vars:
            if not user_edit:
                value = getattr(other, var_name.replace('.', '_'), None)
                if value:
                    setattr(self, var_name.replace('.', '_'), value)

    def write(self, xml_node: waftools_common.minixml.XmlNode) -> None:
        with waftools_common.minixml.XmlNode(xml_node, 'valuemap', attributes=[('type', 'QVariantMap')]) as variant_map:
            for (var_name, user_edit) in self.__class__.published_vars:
                value = getattr(self, var_name.replace('.', '_'), None)
                if value is not None:
                    _write_value(variant_map, value, key=var_name)


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

    def __init__(self, cmake_program: List[str]) -> None:
        if cmake_program:
            self.Id = waftools_common.utils.generate_guid('Motor:cmake')
            self.AutoCreateBuildDirectory = False
            self.AutoDetected = False
            self.AutoRun = True
            self.DetectionSource = ''
            self.DisplayName = 'Motor:cmake'
            self.QchFile = ''
            self.Binary = cmake_program[0]


class QtToolchain(QtObject):
    published_vars = [
        ('ProjectExplorer.CustomToolChain.CompilerPath', False),
        ('ProjectExplorer.CustomToolChain.Cxx11Flags', False),
        ('ProjectExplorer.CustomToolChain.ErrorPattern', False),
        ('ProjectExplorer.CustomToolChain.FileNameCap', False),
        ('ProjectExplorer.CustomToolChain.HeaderPaths', False),
        ('ProjectExplorer.CustomToolChain.LineNumberCap', False),
        ('ProjectExplorer.CustomToolChain.MakePath', True),
        ('ProjectExplorer.CustomToolChain.MessageCap', False),
        ('ProjectExplorer.CustomToolChain.Mkspecs', False),
        ('ProjectExplorer.CustomToolChain.OutputParser', False),
        ('ProjectExplorer.CustomToolChain.PredefinedMacros', False),
        ('ProjectExplorer.CustomToolChain.TargetAbi', False),
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

    @staticmethod
    def get_architecture(env: waflib.ConfigSet.ConfigSet) -> Tuple[str, str]:
        return env.ARCH_FAMILY, env.ARCH_LP64 and '64bit' or '32bit'

    @staticmethod
    def get_platform(env: waflib.ConfigSet.ConfigSet) -> Tuple[str, str]:
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
                os_name = o_name
                break
        else:
            os_name = 'unknown'
        for p, p_name in supported_platform:
            if target.find(p) != -1:
                platform = p_name
                break
        else:
            platform = 'unknown'
        return os_name, platform

    def __init__(
            self,
            language: Optional[int] = None,
            env_name: Optional[str] = None,
            env: Optional[waflib.ConfigSet.ConfigSet] = None
    ) -> None:
        if env_name is not None:
            assert env is not None
            assert language is not None
            arch, variant = self.get_architecture(env)
            os_name, platform = self.get_platform(env)
            abi = '%s-%s-%s-%s-%s' % (arch, os_name, platform, env.DEST_BINFMT, variant)
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
            self.ProjectExplorer_CustomToolChain_Cxx11Flags = ('-std=c++14',)
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
            toolchain_id = 'ProjectExplorer.ToolChain.Custom:%s' % waftools_common.utils.generate_guid(
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
        ('Debugger_Information', False),
    ]

    def __init__(
            self,
            env_name: Optional[str] = None,
            env: Optional[waflib.ConfigSet.ConfigSet] = None,
            toolchain: Optional[QtToolchain] = None
    ) -> None:
        if env_name:
            assert env is not None
            assert toolchain is not None
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
            # abi = getattr(toolchain, 'ProjectExplorer_CustomToolChain_TargetAbi', None)
            # abi = abi or getattr(toolchain, 'ProjectExplorer_GccToolChain_TargetAbi', None)
            # abi = abi or getattr(toolchain, 'ProjectExplorer_MsvcToolChain_TargetAbi', None)
            self.AutoDetected = False
            self.DisplayName = 'Motor:debugger:' + env_name
            self.Id = waftools_common.utils.generate_guid('Motor:debugger:%s' % env_name)


class QtDevice(QtObject):

    def __init__(self) -> None:
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

    def __init__(
            self,
            bld: build_framework.BuildContext,
            env_name: Optional[str] = None,
            env: Optional[waflib.ConfigSet.ConfigSet] = None,
            toolchain_c: Optional[str] = None,
            toolchain_cxx: Optional[str] = None,
            debugger: Optional[str] = None,
            cmake_kit: Optional[str] = None
    ) -> None:
        if env_name:
            assert env is not None
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
                ('CMakeProjectManager.CMakeKitInformation', cmake_kit),
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
            self.PE_Profile_Id = self.guid = waftools_common.utils.generate_guid('Motor:profile:' + env_name)
            self.PE_Profile_MutableInfo = ()
            self.PE_Profile_Name = 'Motor:profile:' + env_name
            self.PE_Profile_SDK = False


def _to_var(name: str) -> str:
    return VAR_PATTERN % name


class QtCreator(build_framework.ProjectGenerator):
    cmd = '_qtcreator'
    PROJECT_TYPE = 'GenericProjectManager.GenericBuildConfiguration'
    version = (0, 0)

    def __init__(self, **kw: Any) -> None:
        build_framework.BuildContext.__init__(self, **kw)
        self.base_node = self.motornode
        self.qt_cmake_tools = []  # type: List[QtCMakeTools]
        self.qt_cmake_tools_to_remove = []  # type: List[QtCMakeTools]
        self.qt_debuggers = []  # type: List[Tuple[str, QtDebugger]]
        self.qt_debuggers_to_remove = []  # type: List[QtDebugger]
        self.qt_toolchains = []  # type: List[Tuple[str, QtToolchain]]
        self.qt_toolchains_to_remove = []  # type: List[QtToolchain]
        self.qt_devices = []  # type: List[QtDevice]
        self.qt_platforms = []  # type: List[Tuple[str, QtPlatform]]
        self.qt_platforms_to_remove = []  # type: List[QtPlatform]

    def load_envs(self) -> None:
        build_framework.ProjectGenerator.load_envs(self)
        self.env.PROJECTS = [self.__class__.cmd]

        self.env.VARIANT = _to_var('Variant')
        self.env.TOOLCHAIN = _to_var('Toolchain')
        self.env.PREFIX = _to_var('Prefix')
        self.env.DEPLOY_ROOTDIR = _to_var('Deploy_RootDir')
        self.env.DEPLOY_BINDIR = _to_var('Deploy_BinDir')
        self.env.DEPLOY_RUNBINDIR = _to_var('Deploy_RunBinDir')
        self.env.DEPLOY_LIBDIR = _to_var('Deploy_LibDir')
        self.env.DEPLOY_INCLUDEDIR = _to_var('Deploy_IncludeDir')
        self.env.DEPLOY_DATADIR = _to_var('Deploy_DataDir')
        self.env.DEPLOY_PLUGINDIR = _to_var('Deploy_PluginDir')
        self.env.DEPLOY_KERNELDIR = _to_var('Deploy_KernelDir')
        build_framework.add_feature(self, 'GUI')

    def execute(self) -> Optional[str]:
        result = build_framework.ProjectGenerator.execute(self)
        if result is not None:
            return result

        self.write_ini_file()
        self.build_platform_list()
        self.write_project_files()
        return None

    @staticmethod
    def write_ini_file() -> None:
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
                        key_list = key.split('\\')
                        if key_list[1] == 'size':
                            delete_index = index
                        else:
                            config_index = int(key_list[1])
                            if max_index is None or config_index > max_index:
                                max_index = config_index
                            if key_list[2] == 'id' and value == '{c75a31ba-e37d-4044-8825-36527d4ceea1}':
                                # found ClangTidy config, nothing to patch
                                return
            if delete_index is not None:
                assert config_line is not None
                del content[delete_index]
                if config_line > delete_index:
                    config_line -= 1
            if config_line is None:
                content += ['[ClangTools]\n', CLANG_TIDY_CONFIG.format(1), 'ClangDiagnosticConfigs\\size=1\n']
            elif max_index is None:
                content[config_line:config_line] = [CLANG_TIDY_CONFIG.format(1), 'ClangDiagnosticConfigs\\size=1\n']
            else:
                content[config_line:config_line] = [CLANG_TIDY_CONFIG.format(max_index + 1),
                                                    'ClangDiagnosticConfigs\\size=%d\n' % (max_index + 1)]

            with open(INI_FILE, 'w') as ini_file:
                ini_file.write(''.join(content))
        except IOError:
            print('QtCreator ini file not found; creating one')
            with open(INI_FILE, 'w') as ini_file:
                ini_file.write('[ClangTools]\n')
                ini_file.write(CLANG_TIDY_CONFIG.format(1))
                ini_file.write('ClangDiagnosticConfigs\\size=1\n')

    def write_project_files(self) -> None:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.srcnode.name)
        self.base_node = self.srcnode.make_node('%s.qtcreator' % appname)
        self.base_node.mkdir()
        try:
            os.makedirs(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp'))
        except OSError:
            pass
        with open(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp', 'motor.xml'), 'w') as codestyle:
            self.write_codestyle(codestyle)

        projects = []
        launcher_project = None  # type: Optional[waflib.Node.Node]
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
                includes, defines = waftools_common.utils.gather_includes_defines(task_gen)
                includes = [waftools_common.utils.path_from(include, self.base_node) for include in includes]
                self.write_includes(task_gen, includes)
                self.write_defines(task_gen, defines)
                node = self.base_node.make_node('%s.creator.user' % task_gen.target)
                with open(node.abspath(), 'w') as f:
                    self.write_user(f, [task_gen])
        assert launcher_project is not None
        self.write_workspace(projects, appname, launcher_project)

    @staticmethod
    def get_environment_id() -> bytearray:
        try:
            with open(os.path.join(HOME_DIRECTORY, '..', 'QtCreator.ini')) as config:
                regexp = re.compile(r'Settings\\EnvironmentId=@ByteArray\((.*)\)$')
                for line in config.readlines():
                    result = regexp.match(line)
                    if result:
                        return bytearray(result.group(1), 'utf-8')
                else:
                    waflib.Logs.warn('QtCreator environment ID not found; creating dummy environment ID')
                    return bytearray(b'{9807fb0e-3785-4641-a197-bb1a10ccc985}')
        except IOError:
            waflib.Logs.warn('QtCreator config not found; creating dummy environment ID')
            return bytearray(b'{9807fb0e-3785-4641-a197-bb1a10ccc985}')

    @staticmethod
    def get_platform_guid(env_name: str) -> str:
        return waftools_common.utils.generate_guid('Motor:profile:' + env_name)

    def load_cmake_tools_list(self) -> None:
        try:
            document = xml.dom.minidom.parse(os.path.join(HOME_DIRECTORY, 'cmaketools.xml'))
        except OSError:
            waflib.Logs.warn('QtCreator cmaketools not found; creating default one')
        else:
            for data in document.getElementsByTagName('data'):
                variable = data.getElementsByTagName('variable')[0]
                variable_name = variable.childNodes[0].toxml().strip()
                if variable_name.startswith('CMakeTools.'):
                    try:
                        int(variable_name[11:])
                    except ValueError:
                        pass
                    else:
                        cmake_tools = QtCMakeTools([])
                        cmake_tools.load_from_node(data.getElementsByTagName('valuemap')[0])
                        self.qt_cmake_tools.append(cmake_tools)
                        if getattr(cmake_tools, 'DisplayName').startswith('Motor:'):
                            self.qt_cmake_tools_to_remove.append(cmake_tools)
        if not self.qt_cmake_tools:
            cmake_program = waflib.Configure.find_program(self, 'cmake', quiet=True, mandatory=False)
            if cmake_program:
                cmake_tool = QtCMakeTools(cmake_program)
                self.qt_cmake_tools.append(cmake_tool)

    def load_debugger_list(self) -> None:
        try:
            document = xml.dom.minidom.parse(os.path.join(HOME_DIRECTORY, 'debuggers.xml'))
        except OSError:
            waflib.Logs.warn('QtCreator debuggers not found; creating default one')
        else:
            for data in document.getElementsByTagName('data'):
                variable = data.getElementsByTagName('variable')[0]
                variable_name = variable.childNodes[0].toxml().strip()
                if variable_name.startswith('DebuggerItem.'):
                    try:
                        int(variable_name[13:])
                    except ValueError:
                        pass
                    else:
                        debugger = QtDebugger()
                        debugger.load_from_node(data.getElementsByTagName('valuemap')[0])
                        self.qt_debuggers.append((debugger.Id, debugger))
                        if debugger.DisplayName.startswith('Motor:'):
                            self.qt_debuggers_to_remove.append(debugger)

    def load_toolchain_list(self) -> None:
        try:
            document = xml.dom.minidom.parse(os.path.join(HOME_DIRECTORY, 'toolchains.xml'))
        except OSError:
            waflib.Logs.warn('QtCreator toolchains not found; creating default one')
        else:
            for data in document.getElementsByTagName('data'):
                variable = data.getElementsByTagName('variable')[0]
                variable_name = variable.childNodes[0].toxml().strip()
                if variable_name.startswith('ToolChain.'):
                    try:
                        int(variable_name[10:])
                    except ValueError:
                        pass
                    else:
                        toolchain = QtToolchain()
                        toolchain.load_from_node(data.getElementsByTagName('valuemap')[0])
                        self.qt_toolchains.append((toolchain.ProjectExplorer_ToolChain_Id, toolchain))
                        if toolchain.ProjectExplorer_ToolChain_DisplayName.startswith('Motor:'):
                            self.qt_toolchains_to_remove.append(toolchain)

    @staticmethod
    def load_device_list() -> None:
        pass

    def load_platform_list(self) -> None:
        try:
            document = xml.dom.minidom.parse(os.path.join(HOME_DIRECTORY, 'profiles.xml'))
        except OSError:
            waflib.Logs.warn('QtCreator profiles not found; creating default one')
        else:
            for data in document.getElementsByTagName('data'):
                variable = data.getElementsByTagName('variable')[0]
                variable_name = variable.childNodes[0].toxml().strip()
                if variable_name.startswith('Profile.'):
                    try:
                        int(variable_name[8:])
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
                            self.qt_platforms.append((platform.PE_Profile_Id, platform))
                            if platform.PE_Profile_Name.startswith('Motor:'):
                                self.qt_platforms_to_remove.append(platform)

    def build_platform_list(self) -> None:
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
            toolchains = []
            for index in (0, 1):
                toolchains.append(QtToolchain(index + 1, env_name, bld_env))

                for t_name, t in self.qt_toolchains:
                    if t_name == toolchains[index].ProjectExplorer_ToolChain_Id:
                        t.copy_from(toolchains[index])
                        toolchains[index] = t
                        try:
                            self.qt_toolchains_to_remove.remove(t)
                        except ValueError:
                            pass
                        break
                else:
                    self.qt_toolchains.append((toolchains[index].ProjectExplorer_ToolChain_Id, toolchains[index]))
            debugger = QtDebugger(env_name, env, toolchains[1])
            for d_name, d in self.qt_debuggers:
                if d_name == debugger.Id:
                    d.copy_from(debugger)
                    self.qt_debuggers_to_remove.remove(d)
                    break
            else:
                self.qt_debuggers.append((debugger.Id, debugger))
            platform = QtPlatform(
                self, env_name, env, toolchains[0].ProjectExplorer_ToolChain_Id,
                toolchains[1].ProjectExplorer_ToolChain_Id, debugger.Id, self.qt_cmake_tools[0].Id
            )
            for p_name, p in self.qt_platforms:
                if p_name == platform.PE_Profile_Id:
                    p.copy_from(platform)
                    self.qt_platforms_to_remove.remove(p)
                    break
            else:
                self.qt_platforms.append((platform.PE_Profile_Id, platform))

        if not os.path.exists(HOME_DIRECTORY):
            os.makedirs(HOME_DIRECTORY)
        with waftools_common.minixml.XmlDocument(
                open(os.path.join(HOME_DIRECTORY, 'profiles.xml'), 'w'), 'UTF-8', [('DOCTYPE', 'QtCreatorProfiles')]
        ) as document:
            with waftools_common.minixml.XmlNode(document, 'qtcreator') as creator:
                profile_index = 0
                for platform_name, platform in self.qt_platforms:
                    if platform not in self.qt_platforms_to_remove:
                        with waftools_common.minixml.XmlNode(creator, 'data') as data:
                            waftools_common.minixml.XmlNode(data, 'variable', 'Profile.%d' % profile_index)
                            platform.write(data)
                        profile_index += 1
                with waftools_common.minixml.XmlNode(creator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'Profile.Count')
                    waftools_common.minixml.XmlNode(data, 'value', str(profile_index), [('type', 'int')])
                with waftools_common.minixml.XmlNode(creator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'Profile.Default')
                    waftools_common.minixml.XmlNode(data, 'value', str(self.qt_platforms[0][1].PE_Profile_Id),
                                                    [('type', 'QString')])
                with waftools_common.minixml.XmlNode(creator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'Version')
                    waftools_common.minixml.XmlNode(data, 'value', '1', [('type', 'int')])

        with waftools_common.minixml.XmlDocument(
                open(os.path.join(HOME_DIRECTORY, 'debuggers.xml'), 'w'), 'UTF-8', [('DOCTYPE', 'QtCreatorDebugger')]
        ) as document:
            with waftools_common.minixml.XmlNode(document, 'qtcreator') as creator:
                debugger_index = 0
                for debugger_name, debugger in self.qt_debuggers:
                    if debugger not in self.qt_debuggers_to_remove:
                        with waftools_common.minixml.XmlNode(creator, 'data') as data:
                            waftools_common.minixml.XmlNode(data, 'variable', 'DebuggerItem.%d' % debugger_index)
                            debugger.write(data)
                        debugger_index += 1
                with waftools_common.minixml.XmlNode(creator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'DebuggerItem.Count')
                    waftools_common.minixml.XmlNode(data, 'value', str(debugger_index), [('type', 'int')])
                with waftools_common.minixml.XmlNode(creator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'Version')
                    waftools_common.minixml.XmlNode(data, 'value', '1', [('type', 'int')])

        with waftools_common.minixml.XmlDocument(
                open(os.path.join(HOME_DIRECTORY, 'cmaketools.xml'), 'w'), 'UTF-8', [('DOCTYPE', 'QtCreatorCMakeTools')]
        ) as document:
            with waftools_common.minixml.XmlNode(document, 'qtcreator') as creator:
                cmaketools_index = 0
                for cmaketools in self.qt_cmake_tools:
                    if cmaketools not in self.qt_cmake_tools_to_remove:
                        with waftools_common.minixml.XmlNode(creator, 'data') as data:
                            waftools_common.minixml.XmlNode(data, 'variable', 'CMakeTools.%d' % cmaketools_index)
                            cmaketools.write(data)
                        cmaketools_index += 1
                with waftools_common.minixml.XmlNode(creator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'CMakeTools.Count')
                    waftools_common.minixml.XmlNode(data, 'value', str(cmaketools_index), [('type', 'int')])
                if self.qt_cmake_tools:
                    with waftools_common.minixml.XmlNode(creator, 'data') as data:
                        waftools_common.minixml.XmlNode(data, 'variable', 'CMakeTools.Default')
                        waftools_common.minixml.XmlNode(data, 'value', str(self.qt_cmake_tools[0].Id),
                                                        [('type', 'QString')])
                with waftools_common.minixml.XmlNode(creator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'Version')
                    waftools_common.minixml.XmlNode(data, 'value', '1', [('type', 'int')])

        with waftools_common.minixml.XmlDocument(
                open(os.path.join(HOME_DIRECTORY, 'toolchains.xml'), 'w'), 'UTF-8', [('DOCTYPE', 'QtCreatorToolChains')]
        ) as document:
            with waftools_common.minixml.XmlNode(document, 'qtcreator') as creator:
                toolchain_index = 0
                for toolchain_name, toolchain in self.qt_toolchains:
                    if toolchain not in self.qt_toolchains_to_remove:
                        with waftools_common.minixml.XmlNode(creator, 'data') as data:
                            waftools_common.minixml.XmlNode(data, 'variable', 'ToolChain.%d' % toolchain_index)
                            toolchain.write(data)
                        toolchain_index += 1
                with waftools_common.minixml.XmlNode(creator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'ToolChain.Count')
                    waftools_common.minixml.XmlNode(data, 'value', str(toolchain_index), [('type', 'int')])
                with waftools_common.minixml.XmlNode(creator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'Version')
                    waftools_common.minixml.XmlNode(data, 'value', '1', [('type', 'int')])

    @staticmethod
    def write_codestyle(file: IO[str]) -> None:
        with waftools_common.minixml.XmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorCodeStyle')]) as cs:
            with waftools_common.minixml.XmlNode(cs, 'qtcreator') as qtcreator:
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'CodeStyleData').close()
                    _write_value(
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
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'DisplayName').close()
                    _write_value(data, 'Motor')

    def write_project(self, task_gen: waflib.TaskGen.task_gen) -> waflib.Node.Node:
        node = self.base_node.make_node('%s.creator' % task_gen.target)
        node.write('[General]')
        return node

    def write_files(self, task_gen: waflib.TaskGen.task_gen) -> None:
        file_list = []
        for _, source_node in getattr(task_gen, 'source_nodes', []):
            file_list += [node.path_from(self.base_node) for node in source_node.ant_glob('**')]
        self.base_node.make_node('%s.files' % task_gen.target).write('\n'.join(file_list))

    def write_includes(self, task_gen: waflib.TaskGen.task_gen, includes: List[str]) -> None:
        self.base_node.make_node('%s.includes' % task_gen.target).write('\n'.join(includes))

    def write_defines(self, task_gen: waflib.TaskGen.task_gen, defines: List[str]) -> None:
        self.base_node.make_node('%s.config' % task_gen.target).write('\n'.join(defines))

    def write_user(self, file: IO[str], task_gens: List[waflib.TaskGen.task_gen]) -> None:
        with waftools_common.minixml.XmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorProject')]) as project:
            with waftools_common.minixml.XmlNode(project, 'qtcreator') as qtcreator:
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'EnvironmentId').close()
                    _write_value(data, self.get_environment_id())
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data_node:
                    waftools_common.minixml.XmlNode(data_node, 'variable',
                                                    'ProjectExplorer.Project.ActiveTarget').close()
                    _write_value(data_node, 0)
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'ProjectExplorer.Project.EditorSettings').close()
                    _write_value(
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
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'ProjectExplorer.Project.PluginSettings').close()
                    _write_value(data, [
                        ('ClangTools', [
                            ('ClangTools.AnalyzeOpenFiles', True),
                            ('ClangTools.BuildBeforeAnalysis', True),
                            ('ClangTools.DiagnosticConfig', '{c75a31ba-e37d-4044-8825-36527d4ceea1}'),
                            ('ClangTools.UseGlobalSettings', False)
                        ])
                    ])
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data:
                    assert self.launcher is not None
                    target_index = 0
                    for env_name in self.env.ALL_TOOLCHAINS:
                        waftools_common.minixml.XmlNode(data, 'variable',
                                                        'ProjectExplorer.Project.Target.%d' % target_index).close()
                        bld_env = self.all_envs[env_name]
                        if bld_env.SUB_TOOLCHAINS:
                            env = self.all_envs[bld_env.SUB_TOOLCHAINS[0]]
                        else:
                            env = bld_env
                        build_configurations = []
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
                                    executable = _to_var('OUT_NAME')
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
                                                _to_var('OUT_DIR')
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
                                                _to_var('RUNBIN_DIR')
                                            ),
                                            (
                                                'ProjectExplorer.ProjectConfiguration.DefaultDisplayName',
                                                'python:%s' % task_gen.target
                                            ),
                                            (
                                                'ProjectExplorer.ProjectConfiguration.DisplayName',
                                                'python:%s' % task_gen.name
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

                        _write_value(
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
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'ProjectExplorer.Project.TargetCount').close()
                    _write_value(data, target_index)
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable',
                                                    'ProjectExplorer.Project.Updater.FileVersion').close()
                    _write_value(data, self.__class__.version[1])
                with waftools_common.minixml.XmlNode(qtcreator, 'data') as data:
                    waftools_common.minixml.XmlNode(data, 'variable', 'Version').close()
                    _write_value(data, self.__class__.version[1])

    def make_build_configuration(
            self,
            build_configuration_index: int,
            bld_env: waflib.ConfigSet.ConfigSet,
            env: waflib.ConfigSet.ConfigSet,
            env_name: str,
            variant: str
    ) -> Tuple[str, List[Any]]:
        assert self.launcher is not None
        options = [a for a in sys.argv if a[0] == '-']
        target_os = _qbs_platform_list(env)
        extra_platform_flags = target_os and [
            ('qbs.targetOS', target_os),
        ] or []
        return (
            'ProjectExplorer.Target.BuildConfiguration.%d' % build_configuration_index, [
                (
                    'ProjectExplorer.BuildConfiguration.BuildDirectory',
                    self.bldnode.make_node(self.variant).abspath()
                ),
                (
                    'GenericProjectManager.GenericBuildConfiguration.BuildDirectory',
                    self.bldnode.make_node(self.variant).abspath()
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
                                        ('qbs.architecture', _qbs_arch(env.TARGET_ARCH)),
                                        ('qbs.targetPlatform', _qbs_platform(env)),
                                    ] + extra_platform_flags
                                ), ('ProjectExplorer.ProjectConfiguration.Id', 'Qbs.BuildStep')
                            ]
                        ),
                        (
                            'ProjectExplorer.BuildStepList.Step.1', [
                                ('ProjectExplorer.BuildStep.Enabled', True),
                                (
                                    'ProjectExplorer.ProcessStep.Arguments',
                                    '%s build:%s:%s %s --werror' %
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

    @staticmethod
    def write_workspace(projects: List[waflib.Node.Node], appname: str, launcher: waflib.Node.Node) -> None:
        workspace_file = os.path.join(HOME_DIRECTORY, '%s.qws' % appname)
        try:
            document = xml.dom.minidom.parse(workspace_file)
        except OSError:
            with waftools_common.minixml.XmlDocument(open(workspace_file, 'w'), 'UTF-8',
                                                     [('DOCTYPE', 'QtCreatorSession')]) as mini_document:
                with waftools_common.minixml.XmlNode(mini_document, 'qtcreator') as creator:
                    with waftools_common.minixml.XmlNode(creator, 'data') as data:
                        waftools_common.minixml.XmlNode(data, 'variable', 'Color').close()
                        waftools_common.minixml.XmlNode(data, 'value', '#666666', [('type', 'QString')]).close()
                    with waftools_common.minixml.XmlNode(creator, 'data') as data:
                        waftools_common.minixml.XmlNode(data, 'variable', 'EditorSettings').close()
                        waftools_common.minixml.XmlNode(data, 'value', '', [('type', 'QByteArray')]).close()
                    with waftools_common.minixml.XmlNode(creator, 'data') as data:
                        waftools_common.minixml.XmlNode(data, 'variable', 'ProjectDependencies').close()
                        waftools_common.minixml.XmlNode(data, 'valuemap', '', [('type', 'QVariantMap')]).close()
                    with waftools_common.minixml.XmlNode(creator, 'data') as data:
                        waftools_common.minixml.XmlNode(data, 'variable', 'ProjectList').close()
                        with waftools_common.minixml.XmlNode(data, 'valuelist', '',
                                                             [('type', 'QVariantList')]) as project_list:
                            for project in projects:
                                waftools_common.minixml.XmlNode(project_list, 'value', project.abspath(),
                                                                [('type', 'QString')]).close()
                    with waftools_common.minixml.XmlNode(creator, 'data') as data:
                        waftools_common.minixml.XmlNode(data, 'variable', 'StartupProject').close()
                        waftools_common.minixml.XmlNode(data, 'value', launcher.abspath(),
                                                        [('type', 'QString')]).close()
                    with waftools_common.minixml.XmlNode(creator, 'data') as data:
                        waftools_common.minixml.XmlNode(data, 'variable', 'valueKeys').close()
                        waftools_common.minixml.XmlNode(data, 'valuelist', '', [('type', 'QVariantList')]).close()
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
                assert isinstance(element.firstChild, xml.dom.minidom.Element)
                if element.firstChild.nodeType == element.firstChild.TEXT_NODE:
                    assert isinstance(element.firstChild, xml.dom.minidom.Text)
                    if element.firstChild.data == 'ProjectList':
                        data = element.parentNode
                        assert isinstance(data, xml.dom.minidom.Element)
                        old_valuelist = data.getElementsByTagName('valuelist')[0]
                        data.replaceChild(new_valuelist, old_valuelist)
            with open(workspace_file, 'w') as new_file:
                new_file.write(document.toxml())


ProjectMap = Dict[str, Union["ProjectMap", waflib.TaskGen.task_gen]]


class Qbs(QtCreator):
    cmd = '_qbs'
    PROJECT_TYPE = 'Qbs.QbsBuildConfiguration'

    def write_project_files(self) -> None:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.srcnode.name)
        self.base_node = self.srcnode
        qbs_project = self.base_node.make_node('%s.qbs' % appname)
        qbs_user = self.base_node.make_node('%s.qbs.user' % appname)
        try:
            os.makedirs(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp'))
        except OSError:
            pass
        with open(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp', 'motor.xml'), 'w') as codestyle:
            self.write_codestyle(codestyle)
        projects = {}  # type: ProjectMap
        project_list = []
        for group in self.groups:
            for task_gen in group:
                if 'motor:kernel' in task_gen.features:
                    continue
                if 'motor:preprocess' in task_gen.features:
                    continue
                task_gen.post()
                try:
                    name = getattr(task_gen, 'module_path').split('.')
                except AttributeError:
                    name = task_gen.name.split('.')
                p = projects
                for c in name[:-1]:
                    try:
                        p_sub = p[c]
                    except KeyError:
                        p_sub = {}
                        p[c] = p_sub
                    assert isinstance(p_sub, dict)
                    p = p_sub
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

    def write_project_list(
            self,
            project_file: IO[str],
            project_list: ProjectMap,
            indent: str = '    '
    ) -> None:
        for k in sorted(project_list.keys()):
            p = project_list[k]
            if isinstance(p, dict):
                project_file.write('%sProject {\n' % indent)
                project_file.write('%s    name: "%s"\n' % (indent, k))
                self.write_project_list(project_file, p, indent + '    ')
                project_file.write('%s}\n' % indent)
            else:
                includes, defines = waftools_common.utils.gather_includes_defines(p)
                includes = [waftools_common.utils.path_from(include, self.base_node) for include in includes]
                project_file.write('%sProduct {\n' % indent)
                project_file.write('%s    Depends { name: "cpp" }\n' % indent)
                for env_name in self.env.ALL_TOOLCHAINS:
                    env = self.all_envs[env_name]
                    if env.SUB_TOOLCHAINS:
                        env = self.all_envs[env.SUB_TOOLCHAINS[0]]
                    if 'android' in env.VALID_PLATFORMS:
                        ndk_root = env.ANDROID_NDK_PATH
                        host_name = os.path.split(os.path.dirname(os.path.dirname(env.CC[0])))[1]
                        project_file.write('%s    Properties\n' % indent)
                        project_file.write('%s    {\n' % indent)
                        project_file.write('%s        condition: qbs.targetOS.includes("android")\n' % indent)
                        project_file.write('%s        Depends { name: "Android.ndk" }\n' % indent)
                        project_file.write('%s        Depends { name: "codesign" }\n' % indent)
                        project_file.write('%s        Android.ndk.hostArch: "%s"\n' % (indent, host_name))
                        project_file.write('%s        Android.ndk.ndkDir: "%s"\n' % (indent, ndk_root))
                        project_file.write(
                            '%s        codesign.debugKeystorePath: "%s"\n' % (indent, env.ANDROID_DEBUGKEY))
                        project_file.write('%s    }\n' % indent)
                        break

                project_file.write('%s    name: "%s"\n' % (indent, p.name))
                project_file.write('%s    targetName: "%s"\n' % (indent, p.name.split('.')[-1]))
                project_file.write('%s    cpp._skipAllChecks: true\n' % (indent,))
                project_file.write('%s    cpp.includePaths: [\n' % indent)
                for include in includes:
                    project_file.write('%s        "%s",\n' % (indent, include.replace('\\', '/')))
                project_file.write('%s    ]\n' % indent)
                project_file.write('%s    cpp.defines: [\n' % indent)
                for define in defines:
                    project_file.write('%s        "%s",\n' % (indent, define))
                project_file.write('%s    ]\n' % indent)
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
    motor_variant = 'projects.qcmake'
    variant = 'projects/qcmake'
    version = (4, 18)

    def __init__(self, **kw: Any) -> None:
        QtCreator.__init__(self, **kw)
        self.cmake_toolchains = {}  # type: Dict[str, str]

    def write_project_files(self) -> None:
        for env_name, toolchain in waftools_common.cmake.write_cmake_workspace(self):
            self.cmake_toolchains[env_name] = toolchain
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

    def make_build_configuration(
            self,
            build_configuration_index: int,
            bld_env: waflib.ConfigSet.ConfigSet,
            env: waflib.ConfigSet.ConfigSet,
            env_name: str,
            variant: str
    ) -> Tuple[str, List[Any]]:
        assert self.launcher is not None
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
                    self.bldnode.make_node('%s/%s/%s' % (self.variant, env_name, variant)).abspath()
                ),
                (
                    'GenericProjectManager.GenericBuildConfiguration.BuildDirectory',
                    self.bldnode.make_node('%s/%s/%s' % (self.variant, env_name, variant)).abspath()
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
    """creates projects for QtCreator 2.x"""
    cmd = 'qtcreator2'
    variant = 'qtcreator2'
    version = (2, 12)


class QtCreator3(QtCreator):
    """creates projects for QtCreator 3.x"""
    cmd = 'qtcreator3'
    variant = 'qtcreator3'
    version = (3, 15)


class QtCreator4(QtCreator):
    """creates projects for QtCreator 4.x"""
    cmd = 'qtcreator4'
    variant = 'qtcreator4'
    version = (4, 18)


class Qbs2(Qbs):
    """creates Qbs projects for QtCreator 2.x"""
    cmd = 'qbs2'
    variant = 'qbs2'
    version = (2, 12)


class Qbs3(Qbs):
    """creates Qbs projects for QtCreator 3.x"""
    cmd = 'qbs3'
    variant = 'qbs3'
    version = (3, 15)


class Qbs4(Qbs):
    """creates Qbs projects for QtCreator 4.x"""
    cmd = 'qbs4'
    variant = 'qbs4'
    version = (4, 18)
