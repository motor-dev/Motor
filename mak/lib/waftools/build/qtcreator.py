import abc
import inspect
import os
import sys
import re
import datetime
import xml.dom.minidom
import build_framework
import waflib.Task
import waflib.TaskGen
from typing import Any, Dict, IO, Iterable, List, Optional, Tuple, Type, Union
from types import TracebackType


def _xmlify(s: str) -> str:
    s = s.replace("&", "&amp;")  # do this first
    s = s.replace("'", "&apos;")
    s = s.replace('"', "&quot;")
    return s


class MiniXmlDocument(object):
    def __init__(
            self,
            file: IO[str],
            encoding: str,
            processing_instructions: Optional[List[Tuple[str, str]]] = None
    ) -> None:
        self.file = file
        self.file.write('<?xml version="1.0" encoding="%s" standalone="no"?>\n' % encoding)
        if processing_instructions is not None:
            for instruction in processing_instructions:
                self.file.write('<!%s %s>\n' % instruction)
        self.closed = False
        self.empty = False
        self.current = None  # type: Optional["MiniXmlNode"]
        self.indent = -1

    def __enter__(self) -> "MiniXmlDocument":
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> Optional[bool]:
        self.close()
        return None

    def close(self) -> None:
        self.file.close()

    def add(self, node: "MiniXmlNode") -> None:
        assert not self.closed
        assert self.current is None
        if self.empty:
            self.begin()
        self.empty = False
        self.current = node

    def begin(self) -> None:
        raise NotImplementedError


class MiniXmlNode(object):
    def __init__(
            self,
            parent: Union[MiniXmlDocument, "MiniXmlNode"],
            name: str,
            text: str = '',
            attributes: Union[None, Iterable[Tuple[str, str]]] = None) -> None:
        self.parent = parent
        self.current = None  # type: Optional["MiniXmlNode"]
        self.name = name
        self.indent = parent.indent + 1  # type: int
        self.file = parent.file  # type: IO[str]
        self.closed = False
        self.empty = True
        parent.add(self)
        self.open(text, attributes)

    def __enter__(self) -> "MiniXmlNode":
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> Optional[bool]:
        if not self.closed:
            self.close()
        return None

    def add(self, node: "MiniXmlNode") -> None:
        assert not self.closed
        assert self.current is None
        if self.empty:
            self.begin()
        self.empty = False
        self.current = node

    def open(self, text: str = '', attributes: Union[None, Iterable[Tuple[str, str]]] = None) -> None:
        self.file.write('%s<%s' % (' ' * self.indent, self.name))
        if attributes:
            if isinstance(attributes, dict):
                for key, value in attributes.items():
                    self.file.write(' %s="%s"' % (key, value))
            else:
                for key, value in attributes:
                    self.file.write(' %s="%s"' % (key, value))
        if text:
            self.file.write('>%s</%s>\n' % (_xmlify(text), self.name))
            assert (self.parent.current == self)
            self.parent.current = None
            self.closed = True
            self.empty = False

    def close(self) -> None:
        if not self.closed:
            assert (self.parent.current == self)
            self.parent.current = None
            if self.empty:
                self.file.write(' />\n')
            else:
                self.file.write('%s</%s>\n' % (' ' * self.indent, self.name))

    def begin(self) -> None:
        self.file.write('>\n')
        self.empty = False


if sys.platform == 'win32':
    HOME_DIRECTORY = os.path.join(os.getenv('APPDATA'), 'QtProject', 'qtcreator')
    INI_FILE = os.path.join(os.getenv('APPDATA'), 'QtProject', 'QtCreator.ini')
else:
    HOME_DIRECTORY = os.path.join(os.path.expanduser('~'), '.config', 'QtProject', 'qtcreator')
    INI_FILE = os.path.join(os.path.expanduser('~'), '.config', 'QtProject', 'QtCreator.ini')

CLANG_TIDY_CONFIG = "ClangDiagnosticConfigs\\{0}\\clangTidyChecks=\n" \
                    "ClangDiagnosticConfigs\\{0}\\clangTidyChecksOptions=@Variant(\\0\\0\\0\\b\\0\\0\\0\\0)\n" \
                    "ClangDiagnosticConfigs\\{0}\\clangTidyMode=2\n" \
                    "ClangDiagnosticConfigs\\{0}\\clazyChecks=\n" \
                    "ClangDiagnosticConfigs\\{0}\\clazyMode=0\n" \
                    "ClangDiagnosticConfigs\\{0}\\diagnosticOptions=-w\n" \
                    "ClangDiagnosticConfigs\\{0}\\displayName=Motor\n" \
                    "ClangDiagnosticConfigs\\{0}\\id={{c75a31ba-e37d-4044-8825-36527d4ceea1}}\n" \
                    "ClangDiagnosticConfigs\\{0}\\useBuildSystemFlags=false\n"


def _get_environment_id() -> bytearray:
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


def _get_platform_guid(env_name: str) -> str:
    return build_framework.generate_guid('Motor:profile:' + env_name)


def _qbs_arch(arch_name: str) -> str:
    archs = {'amd64': 'x86_64', 'x64': 'x86_64', 'x86_amd64': 'x86_64', 'aarch64': 'arm64', 'ppc64le': 'ppc64'}
    return archs.get(arch_name, arch_name)


def _qbs_platform(env: waflib.ConfigSet.ConfigSet) -> str:
    if 'iphonesimulator' in env.VALID_PLATFORMS:
        return 'ios-simulator'
    elif 'iphone' in env.VALID_PLATFORMS:
        return 'ios'
    else:
        return env.VALID_PLATFORMS[0]


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


def _write_value(node: MiniXmlNode, value: Any, key: str = '') -> None:
    value_type, strvalue = _convert_value(key, value)
    attrs = [('type', value_type)]
    if key:
        attrs.append(('key', key))
    if isinstance(value, tuple):
        with MiniXmlNode(node, 'valuelist', strvalue, attrs) as value_list:
            for v in value:
                _write_value(value_list, v)
    elif isinstance(value, list):
        with MiniXmlNode(node, 'valuemap', strvalue, attrs) as value_map:
            for key, v in value:
                _write_value(value_map, v, key)
    else:
        MiniXmlNode(node, 'value', strvalue, attrs).close()


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

    def write(self, xml_node: MiniXmlNode) -> None:
        with MiniXmlNode(xml_node, 'valuemap',
                         attributes=[('type', 'QVariantMap')]) as variant_map:
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
            self.Id = build_framework.generate_guid('Motor:cmake')
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
        ('ProjectExplorer.MsvcToolChain.environmentModifications', False),
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
            ('darwin', 'darwin'),
        )
        supported_platform = (
            ('android', 'android'),
            ('mingw', 'msys'),
            ('windows-gnu', 'msys'),
            ('msvc14', 'msvc2015'),
            ('msvc15', 'msvc2017'),
            ('msvc16', 'msvc2019'),
            ('msvc17', 'msvc2022'),
            ('msvc', 'msvc2013'),
            ('freebsd', 'freebsd'),
            ('darwin', 'generic'),
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

        supported_abis = (
            ('mac-o', 'mach_o'),
        )
        for abi, a_name in supported_abis:
            if env.DEST_BINFMT.find(abi) != -1:
                abi = a_name
                break
        else:
            abi = env.DEST_BINFMT
        return os_name, platform, abi

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
            os_name, platform, abi = self.get_platform(env)
            abi = '%s-%s-%s-%s-%s' % (arch, os_name, platform, abi, variant)
            compiler = env.CC if language == 1 else env.CXX
            original_flags = env.CFLAGS[:] if language == 1 else env.CXXFLAGS[:]
            flags = []
            while original_flags:
                f = original_flags.pop(0)
                if f == '-target':
                    f = original_flags.pop(0)
                    flags.append('--target=%s' % f)
                else:
                    flags.append(f)
            flags.append('-DTOOLCHAIN=%s' % env_name)
            if isinstance(compiler, list):
                flags = compiler[1:] + flags
                compiler = compiler[0]

            if env.COMPILER_NAME == 'gcc':
                self.ProjectExplorer_GccToolChain_Path = compiler
                self.ProjectExplorer_GccToolChain_TargetAbi = abi
                self.ProjectExplorer_GccToolChain_PlatformCodeGenFlags = tuple(flags)
                self.ProjectExplorer_GccToolChain_PlatformLinkerFlags = tuple()
                if platform == 'android':
                    toolchain_id = 'Qt4ProjectManager.ToolChain.Android:%s' % build_framework.generate_guid(
                        'Motor:toolchain:%s:%d' % (env_name, language)
                    )
                    self.Qt4ProjectManager_Android_NDK_TC_VERION = env_name.split('-')[-1]
                else:
                    toolchain_id = 'ProjectExplorer.ToolChain.Gcc:%s' % build_framework.generate_guid(
                        'Motor:toolchain:%s:%d' % (env_name, language)
                    )
            elif env.COMPILER_NAME in ('clang', 'llvm'):
                self.ProjectExplorer_GccToolChain_Path = compiler
                self.ProjectExplorer_GccToolChain_TargetAbi = abi
                self.ProjectExplorer_GccToolChain_PlatformCodeGenFlags = tuple(flags)
                self.ProjectExplorer_GccToolChain_PlatformLinkerFlags = tuple()
                if platform == 'android':
                    toolchain_id = 'Qt4ProjectManager.ToolChain.Android:%s' % build_framework.generate_guid(
                        'Motor:toolchain:%s:%d' % (env_name, language)
                    )
                    self.Qt4ProjectManager_Android_NDK_TC_VERION = env_name.split('-')[-1]
                else:
                    toolchain_id = 'ProjectExplorer.ToolChain.Clang:%s' % build_framework.generate_guid(
                        'Motor:toolchain:%s:%d' % (env_name, language)
                    )
            elif env.COMPILER_NAME == 'icc':
                self.ProjectExplorer_GccToolChain_Path = compiler
                self.ProjectExplorer_GccToolChain_TargetAbi = abi
                toolchain_id = 'ProjectExplorer.ToolChain.LinuxIcc:%s' % build_framework.generate_guid(
                    'Motor:toolchain:%s:%d' % (env_name, language)
                )
            elif env.COMPILER_NAME == 'suncc':
                self.ProjectExplorer_GccToolChain_Path = compiler
                self.ProjectExplorer_GccToolChain_TargetAbi = abi
                self.ProjectExplorer_GccToolChain_PlatformCodeGenFlags = tuple(flags)
                self.ProjectExplorer_GccToolChain_PlatformLinkerFlags = tuple()
                toolchain_id = 'ProjectExplorer.ToolChain.Gcc:%s' % build_framework.generate_guid(
                    'Motor:toolchain:%s:%d' % (env_name, language)
                )
            elif env.COMPILER_NAME == 'msvc' and env.MSVC_COMPILER != 'intel':
                self.ProjectExplorer_MsvcToolChain_VarsBat = env.MSVC_BATFILE[0].replace('\\', '/')
                self.ProjectExplorer_MsvcToolChain_VarsBatArg = env.MSVC_BATFILE[1] or ''
                self.ProjectExplorer_MsvcToolChain_SupportedAbi = abi
                toolchain_id = 'ProjectExplorer.ToolChain.Msvc:%s' % build_framework.generate_guid(
                    'Motor:toolchain:%s:%d' % (env_name, language)
                )
                self.ProjectExplorer_MsvcToolChain_environmentModifications = tuple(
                    (variable, 0, value) for variable, value in env.MSVC_ENV.items()
                )
            else:
                if compiler == 1:
                    defines = env.COMPILER_C_DEFINES
                    includes = env.COMPILER_C_INCLUDES
                else:
                    defines = env.COMPILER_CXX_DEFINES
                    includes = env.COMPILER_CXX_INCLUDES
                self.ProjectExplorer_CustomToolChain_CompilerPath = compiler
                self.ProjectExplorer_CustomToolChain_Cxx11Flags = tuple(flags + ['-std=c++14'])
                self.ProjectExplorer_CustomToolChain_ErrorPattern = ''
                self.ProjectExplorer_CustomToolChain_FileNameCap = 1
                self.ProjectExplorer_CustomToolChain_HeaderPaths = tuple(
                    i.replace('\\', '/') for i in includes
                )
                self.ProjectExplorer_CustomToolChain_LineNumberCap = 2
                self.ProjectExplorer_CustomToolChain_MakePath = ''
                self.ProjectExplorer_CustomToolChain_MessageCap = 3
                self.ProjectExplorer_CustomToolChain_Mkspecs = ''
                self.ProjectExplorer_CustomToolChain_OutputParser = 0
                toolchain_id = 'ProjectExplorer.ToolChain.Custom:%s' % build_framework.generate_guid(
                    'Motor:toolchain:%s:%d' % (env_name, language)
                )
                self.ProjectExplorer_CustomToolChain_PredefinedMacros = tuple(
                    '#define %s' % ' '.join(d.split('=', 1)) for d in defines)
                self.ProjectExplorer_CustomToolChain_TargetAbi = abi
            self.ProjectExplorer_ToolChain_Language = language
            self.ProjectExplorer_ToolChain_Autodetect = False
            self.ProjectExplorer_ToolChain_DisplayName = 'Motor:toolchain:' + env_name
            self.ProjectExplorer_ToolChain_Id = toolchain_id


class QtDebugger(QtObject):
    published_vars = [
        ('Abis', False),
        ('AutoDetected', False),
        ('Binary', False),
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
                if env.ARCH_NAME == 'amd64':
                    self.Abis = ('x86-windows-msvc2017-pe-64bit',)
                elif env.ARCH_NAME == 'x86':
                    self.Abis = ('x86-windows-msvc2017-pe-32bit',)
                elif env.ARCH_NAME == 'arm64':
                    self.Abis = ('arm-windows-msvc2017-pe-64bit',)
                elif env.ARCH_NAME.startswith('arm'):
                    self.Abis = ('arm-windows-msvc2017-pe-32bit',)
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
            self.Id = build_framework.generate_guid('Motor:debugger:%s' % env_name)


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
            self.PE_Profile_Id = self.guid = build_framework.generate_guid('Motor:profile:' + env_name)
            self.PE_Profile_MutableInfo = ()
            self.PE_Profile_Name = 'Motor:profile:' + env_name
            self.PE_Profile_SDK = False


class qtcreator_codestyle(waflib.Task.Task):
    color = 'PINK'
    always_run = True

    def run(self) -> Optional[int]:
        try:
            os.makedirs(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp'))
        except OSError:
            pass
        with open(os.path.join(HOME_DIRECTORY, 'codestyles', 'Cpp', 'motor.xml'), 'w') as codestyle:
            with MiniXmlDocument(codestyle, 'UTF-8', [('DOCTYPE', 'QtCreatorCodeStyle')]) as cs:
                with MiniXmlNode(cs, 'qtcreator') as qtcreator:
                    with MiniXmlNode(qtcreator, 'data') as data:
                        MiniXmlNode(data, 'variable', 'CodeStyleData').close()
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
                    with MiniXmlNode(qtcreator, 'data') as data:
                        MiniXmlNode(data, 'variable', 'DisplayName').close()
                        _write_value(data, 'Motor')
        return None


class qtcreator_config(waflib.Task.Task):
    color = 'PINK'
    always_run = True

    def run(self) -> Optional[int]:
        build_context = self.generator.bld
        assert isinstance(build_context, build_framework.BuildContext)
        qt_cmake_tools = []  # type: List[QtCMakeTools]
        qt_cmake_tools_to_remove = []  # type: List[QtCMakeTools]
        qt_debuggers = []  # type: List[Tuple[str, QtDebugger]]
        qt_debuggers_to_remove = []  # type: List[QtDebugger]
        qt_toolchains = []  # type: List[Tuple[str, QtToolchain]]
        qt_toolchains_to_remove = []  # type: List[QtToolchain]
        qt_devices = []  # type: List[QtDevice]
        qt_platforms = []  # type: List[Tuple[str, QtPlatform]]
        qt_platforms_to_remove = []  # type: List[QtPlatform]

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
                        qt_cmake_tools.append(cmake_tools)
                        if getattr(cmake_tools, 'DisplayName').startswith('Motor:'):
                            qt_cmake_tools_to_remove.append(cmake_tools)
        if not qt_cmake_tools:
            cmake_program = waflib.Configure.find_program(build_context, 'cmake', quiet=True, mandatory=False)
            if cmake_program:
                cmake_tool = QtCMakeTools(cmake_program)
                qt_cmake_tools.append(cmake_tool)
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
                        qt_debuggers.append((debugger.Id, debugger))
                        if debugger.DisplayName.startswith('Motor:'):
                            qt_debuggers_to_remove.append(debugger)
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
                        qt_toolchains.append((toolchain.ProjectExplorer_ToolChain_Id, toolchain))
                        if toolchain.ProjectExplorer_ToolChain_DisplayName.startswith('Motor:'):
                            qt_toolchains_to_remove.append(toolchain)

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
                        platform = QtPlatform(build_context, '')
                        platform.load_from_node(data.getElementsByTagName('valuemap')[0])
                        try:
                            platform.guid = platform.PE_Profile_Id
                        except AttributeError:
                            pass
                        else:
                            qt_platforms.append((platform.PE_Profile_Id, platform))
                            if platform.PE_Profile_Name.startswith('Motor:'):
                                qt_platforms_to_remove.append(platform)

        for env_name in self.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[env_name]
            if env.SUB_TOOLCHAINS:
                bld_env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
            else:
                bld_env = env
            toolchains = []
            for index in (0, 1):
                toolchains.append(QtToolchain(index + 1, env_name, bld_env))

                for t_name, t in qt_toolchains:
                    if t_name == toolchains[index].ProjectExplorer_ToolChain_Id:
                        t.copy_from(toolchains[index])
                        toolchains[index] = t
                        try:
                            qt_toolchains_to_remove.remove(t)
                        except ValueError:
                            pass
                        break
                else:
                    qt_toolchains.append((toolchains[index].ProjectExplorer_ToolChain_Id, toolchains[index]))
            debugger = QtDebugger(env_name, env, toolchains[1])
            for d_name, d in qt_debuggers:
                if d_name == debugger.Id:
                    d.copy_from(debugger)
                    qt_debuggers_to_remove.remove(d)
                    break
            else:
                qt_debuggers.append((debugger.Id, debugger))
            platform = QtPlatform(
                build_context, env_name, env, toolchains[0].ProjectExplorer_ToolChain_Id,
                toolchains[1].ProjectExplorer_ToolChain_Id, debugger.Id, qt_cmake_tools[0].Id
            )
            for p_name, p in qt_platforms:
                if p_name == platform.PE_Profile_Id:
                    p.copy_from(platform)
                    qt_platforms_to_remove.remove(p)
                    break
            else:
                qt_platforms.append((platform.PE_Profile_Id, platform))

        with open(self.outputs[0].abspath(), 'w') as file:
            with MiniXmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorProfiles')]) as out_document:
                with MiniXmlNode(out_document, 'qtcreator') as creator:
                    profile_index = 0
                    for platform_name, platform in qt_platforms:
                        if platform not in qt_platforms_to_remove:
                            with MiniXmlNode(creator, 'data') as out_data:
                                MiniXmlNode(out_data, 'variable', 'Profile.%d' % profile_index)
                                platform.write(out_data)
                            profile_index += 1
                    with MiniXmlNode(creator, 'data') as out_data:
                        MiniXmlNode(out_data, 'variable', 'Profile.Count')
                        MiniXmlNode(out_data, 'value', str(profile_index), [('type', 'int')])
                    with MiniXmlNode(creator, 'data') as out_data:
                        MiniXmlNode(out_data, 'variable', 'Profile.Default')
                        MiniXmlNode(out_data, 'value', str(qt_platforms[0][1].PE_Profile_Id),
                                    [('type', 'QString')])
                    with MiniXmlNode(creator, 'data') as out_data:
                        MiniXmlNode(out_data, 'variable', 'Version')
                        MiniXmlNode(out_data, 'value', '1', [('type', 'int')])

        with open(self.outputs[1].abspath(), 'w') as file:
            with MiniXmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorDebugger')]) as out_document:
                with MiniXmlNode(out_document, 'qtcreator') as creator:
                    debugger_index = 0
                    for debugger_name, debugger in qt_debuggers:
                        if debugger not in qt_debuggers_to_remove:
                            with MiniXmlNode(creator, 'data') as out_data:
                                MiniXmlNode(out_data, 'variable', 'DebuggerItem.%d' % debugger_index)
                                debugger.write(out_data)
                            debugger_index += 1
                    with MiniXmlNode(creator, 'data') as out_data:
                        MiniXmlNode(out_data, 'variable', 'DebuggerItem.Count')
                        MiniXmlNode(out_data, 'value', str(debugger_index), [('type', 'int')])
                    with MiniXmlNode(creator, 'data') as out_data:
                        MiniXmlNode(out_data, 'variable', 'Version')
                        MiniXmlNode(out_data, 'value', '1', [('type', 'int')])

        with open(self.outputs[2].abspath(), 'w') as file:
            with MiniXmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorCMakeTools')]) as out_document:
                with MiniXmlNode(out_document, 'qtcreator') as creator:
                    cmaketools_index = 0
                    for cmaketools in qt_cmake_tools:
                        if cmaketools not in qt_cmake_tools_to_remove:
                            with MiniXmlNode(creator, 'data') as out_data:
                                MiniXmlNode(out_data, 'variable', 'CMakeTools.%d' % cmaketools_index)
                                cmaketools.write(out_data)
                            cmaketools_index += 1
                    with MiniXmlNode(creator, 'data') as out_data:
                        MiniXmlNode(out_data, 'variable', 'CMakeTools.Count')
                        MiniXmlNode(out_data, 'value', str(cmaketools_index), [('type', 'int')])
                    if qt_cmake_tools:
                        with MiniXmlNode(creator, 'data') as out_data:
                            MiniXmlNode(out_data, 'variable', 'CMakeTools.Default')
                            MiniXmlNode(out_data, 'value', str(qt_cmake_tools[0].Id),
                                        [('type', 'QString')])
                    with MiniXmlNode(creator, 'data') as out_data:
                        MiniXmlNode(out_data, 'variable', 'Version')
                        MiniXmlNode(out_data, 'value', '1', [('type', 'int')])

        with open(self.outputs[3].abspath(), 'w') as file:
            with MiniXmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorToolChains')]) as out_document:
                with MiniXmlNode(out_document, 'qtcreator') as creator:
                    toolchain_index = 0
                    for toolchain_name, toolchain in qt_toolchains:
                        if toolchain not in qt_toolchains_to_remove:
                            with MiniXmlNode(creator, 'data') as out_data:
                                MiniXmlNode(out_data, 'variable', 'ToolChain.%d' % toolchain_index)
                                toolchain.write(out_data)
                            toolchain_index += 1
                    with MiniXmlNode(creator, 'data') as out_data:
                        MiniXmlNode(out_data, 'variable', 'ToolChain.Count')
                        MiniXmlNode(out_data, 'value', str(toolchain_index), [('type', 'int')])
                    with MiniXmlNode(creator, 'data') as out_data:
                        MiniXmlNode(out_data, 'variable', 'Version')
                        MiniXmlNode(out_data, 'value', '1', [('type', 'int')])

        return None


class qtcreator_ini(waflib.Task.Task):
    color = 'PINK'
    always_run = True

    def run(self) -> Optional[int]:
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
                                return None
        except IOError:
            print('QtCreator ini file not found; creating one')
            with open(INI_FILE, 'w') as ini_file:
                ini_file.write('[ClangTools]\n')
                ini_file.write(CLANG_TIDY_CONFIG.format(1))
                ini_file.write('ClangDiagnosticConfigs\\size=1\n')
        else:
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

        return None


class qtcreator_user(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        self.m.update(str([a for a in sys.argv if a[0] == '-']).encode())
        self.m.update(getattr(self.generator.bld, 'launcher').target.encode())
        build_context = self.generator.bld
        for env_name in build_context.env.ALL_TOOLCHAINS:
            bld_env = build_context.all_envs[env_name]
            if bld_env.SUB_TOOLCHAINS:
                env = build_context.all_envs[bld_env.SUB_TOOLCHAINS[0]]
            else:
                env = bld_env
            self.m.update(env_name.encode())

    @abc.abstractmethod
    def make_build_configuration(
            self,
            build_configuration_index: int,
            bld_env: waflib.ConfigSet.ConfigSet,
            env: waflib.ConfigSet.ConfigSet,
            env_name: str,
            variant: str
    ) -> Tuple[str, List[Any]]:
        raise NotImplemented

    def run(self) -> Optional[int]:
        build_context = self.generator.bld
        assert isinstance(build_context, build_framework.BuildContext)
        project_list = []
        for group in build_context.groups:
            for task_gen in group:
                if 'motor:kernel' in task_gen.features:
                    continue
                if 'motor:preprocess' in task_gen.features:
                    continue
                project_list.append(task_gen)

        with open(self.outputs[0].abspath(), 'w') as file:
            with MiniXmlDocument(file, 'UTF-8', [('DOCTYPE', 'QtCreatorProject')]) as project:
                with MiniXmlNode(project, 'qtcreator') as qtcreator:
                    with MiniXmlNode(qtcreator, 'data') as data:
                        MiniXmlNode(data, 'variable', 'EnvironmentId').close()
                        _write_value(data, _get_environment_id())
                    with MiniXmlNode(qtcreator, 'data') as data_node:
                        MiniXmlNode(data_node, 'variable',
                                    'ProjectExplorer.Project.ActiveTarget').close()
                        _write_value(data_node, 0)
                    with MiniXmlNode(qtcreator, 'data') as data:
                        MiniXmlNode(data, 'variable',
                                    'ProjectExplorer.Project.EditorSettings').close()
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
                    with MiniXmlNode(qtcreator, 'data') as data:
                        MiniXmlNode(data, 'variable',
                                    'ProjectExplorer.Project.PluginSettings').close()
                        _write_value(data, [
                            ('ClangTools', [
                                ('ClangTools.AnalyzeOpenFiles', True),
                                ('ClangTools.BuildBeforeAnalysis', False),
                                ('ClangTools.DiagnosticConfig', '{c75a31ba-e37d-4044-8825-36527d4ceea1}'),
                                ('ClangTools.UseGlobalSettings', False)
                            ])
                        ])
                    with MiniXmlNode(qtcreator, 'data') as data:
                        assert build_context.launcher is not None
                        target_index = 0
                        for env_name in build_context.env.ALL_TOOLCHAINS:
                            MiniXmlNode(data, 'variable',
                                        'ProjectExplorer.Project.Target.%d' % target_index).close()
                            bld_env = build_context.all_envs[env_name]
                            if bld_env.SUB_TOOLCHAINS:
                                env = build_context.all_envs[bld_env.SUB_TOOLCHAINS[0]]
                            else:
                                env = bld_env
                            build_configurations = []
                            build_configuration_index = 0
                            for variant in build_context.env.ALL_VARIANTS:
                                build_configurations.append(
                                    self.make_build_configuration(build_configuration_index, bld_env, env, env_name,
                                                                  variant))
                                build_configuration_index += 1
                            run_configurations = []
                            index = 0
                            for task_gen in project_list:
                                if 'motor:game' in task_gen.features:
                                    if 'android' in env.VALID_PLATFORMS:
                                        executable = env.ADB[0]
                                        arguments = 'shell am start com.motor/.MotorActivity --es %s' % task_gen.target
                                    else:
                                        arguments = task_gen.target
                                        executable = os.path.join(
                                            build_context.srcnode.abspath(), bld_env.PREFIX,
                                            '%{ActiveProject:BuildConfig:Name}', env.DEPLOY_BINDIR,
                                            env.cxxprogram_PATTERN % build_context.launcher.target
                                        )
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
                                                ('ProjectExplorer.CustomExecutableRunConfiguration.Executable',
                                                 executable),
                                                ('ProjectExplorer.CustomExecutableRunConfiguration.UseTerminal', False),
                                                (
                                                    'ProjectExplorer.ProjectConfiguration.DefaultDisplayName',
                                                    'Run %s' % task_gen.target
                                                ),
                                                (
                                                    'ProjectExplorer.ProjectConfiguration.DisplayName',
                                                    '%s:%s' % (build_context.launcher.target, task_gen.name)
                                                ),
                                                (
                                                    'ProjectExplorer.ProjectConfiguration.Id',
                                                    'ProjectExplorer.CustomExecutableRunConfiguration'
                                                ),
                                                ('RunConfiguration.Arguments', arguments),
                                                (
                                                    'RunConfiguration.WorkingDirectory',
                                                    os.path.join(build_context.srcnode.abspath(), bld_env.PREFIX,
                                                                 '%{ActiveProject:BuildConfig:Name}')
                                                ),
                                                ('RunConfiguration.QmlDebugServerPort', 3768),
                                                ('RunConfiguration.UseCppDebugger', True),
                                                ('RunConfiguration.UseCppDebuggerAuto', True),
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
                                                    os.path.join(
                                                        build_context.srcnode.abspath(), bld_env.PREFIX, variant,
                                                        env.DEPLOY_RUNBINDIR
                                                    )
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
                                                ('RunConfiguration.UseCppDebuggerAuto', True),
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
                                          ('ProjectExplorer.ProjectConfiguration.Id', _get_platform_guid(env_name)),
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
                    with MiniXmlNode(qtcreator, 'data') as data:
                        MiniXmlNode(data, 'variable',
                                    'ProjectExplorer.Project.TargetCount').close()
                        _write_value(data, target_index)
                    with MiniXmlNode(qtcreator, 'data') as data:
                        MiniXmlNode(data, 'variable',
                                    'ProjectExplorer.Project.Updater.FileVersion').close()
                        _write_value(data, 18)
                    with MiniXmlNode(qtcreator, 'data') as data:
                        MiniXmlNode(data, 'variable', 'Version').close()
                        _write_value(data, 18)

        return None


_ProjectMap = Dict[str, Tuple["_ProjectMap", Optional[waflib.TaskGen.task_gen]]]


class qbs(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        waflib.Task.Task.sig_vars(self)
        projects = getattr(self, 'projects')  # type: _ProjectMap
        build_context = self.generator.bld

        def sig_project(project_list: _ProjectMap) -> None:
            for k in sorted(project_list.keys()):
                self.m.update(k.encode())
                p, tg = project_list[k]
                sig_project(p)
                if tg is not None:
                    defines = tg.env.DEFINES
                    includes = [include.path_from(build_context.srcnode) for include in getattr(tg, 'includes_nodes')]
                    source_nodes = [str(n) for _, source_node in getattr(tg, 'source_nodes') for n in
                                    (source_node.ant_glob('**') if source_node.isdir() else [source_node])]
                    self.m.update((tg.name + ';'.join(defines + includes + source_nodes)).encode())

        sig_project(projects)
        self.m.update(inspect.getsource(self.write_project_list).encode())

    def run(self) -> Optional[int]:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, self.generator.bld.srcnode.name)
        projects = getattr(self, 'projects')  # type: _ProjectMap

        with open(self.outputs[0].abspath(), 'w') as pfile:
            pfile.write(
                'import qbs\n\n'
                'Project {\n'
                '    name: "%s"\n'
                '    property string toolchain: undefined\n'
                '' % appname
            )
            self.write_project_list(pfile, projects)
            pfile.write('}\n')

        return None

    def write_project_list(
            self,
            project_file: IO[str],
            project_list: _ProjectMap,
            indent: str = '    '
    ) -> None:
        build_context = self.generator.bld
        for k in sorted(project_list.keys()):
            p, tg = project_list[k]
            if p:
                project_file.write('%sProject {\n' % indent)
                project_file.write('%s    name: "%s"\n' % (indent, k))
                self.write_project_list(project_file, p, indent + '    ')
                project_file.write('%s}\n' % indent)
            if tg is not None:
                defines = tg.env.DEFINES
                includes = [include.path_from(build_context.srcnode) for include in getattr(tg, 'includes_nodes')]
                project_file.write('%sProduct {\n' % indent)
                project_file.write('%s    qbsSearchPaths: "%s/qbs/qbs/" + project.toolchain\n' % (
                    indent, build_context.bldnode.path_from(build_context.path)
                ))
                project_file.write('%s    Depends { name: "motor_module" }\n' % indent)
                project_file.write('%s    Depends { name: "cpp" }\n' % indent)
                for env_name in build_context.env.ALL_TOOLCHAINS:
                    env = build_context.all_envs[env_name]
                    if env.SUB_TOOLCHAINS:
                        env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
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

                project_file.write('%s    name: "%s"\n' % (indent, tg.name))
                project_file.write('%s    targetName: "%s"\n' % (indent, tg.name.split('.')[-1]))
                project_file.write('%s    type: "Dummy"\n' % (indent,))
                project_file.write('%s    cpp.cxxLanguageVersion: "c++14"\n' % (indent,))
                project_file.write('%s    cpp.includePaths: motor_module.includePaths.concat([\n' % indent)
                for include in includes:
                    project_file.write('%s        "%s",\n' % (indent, include.replace('\\', '/')))
                project_file.write('%s    ])\n' % indent)
                project_file.write('%s    cpp.defines: motor_module.defines.concat([\n' % indent)
                for define in defines:
                    project_file.write('%s        "%s",\n' % (indent, define))
                project_file.write('%s    ])\n' % indent)
                project_file.write('%s    files: [\n' % indent)
                delayed = []
                for name, source_node in getattr(tg, 'source_nodes', []):
                    if source_node.isdir():
                        for node in source_node.ant_glob('**/*', excl=['kernels/**', 'tests/**', '**/*.pyc'],
                                                         remove=False):
                            if build_framework.apply_source_filter(tg, tg.env, node)[1]:
                                delayed.append(node)
                            else:
                                node_path = node.path_from(build_context.srcnode).replace('\\', '/')
                                project_file.write('%s        "%s",\n' % (indent, node_path))
                    else:
                        node_path = source_node.path_from(build_context.srcnode).replace('\\', '/')
                        project_file.write('%s        "%s",\n' % (indent, node_path))
                project_file.write('%s    ]\n' % indent)
                for env_name in build_context.env.ALL_TOOLCHAINS:
                    env = build_context.all_envs[env_name]
                    if env.SUB_TOOLCHAINS:
                        env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
                    active = []
                    for node in delayed:
                        if build_framework.apply_source_filter(tg, env, node)[0]:
                            active.append(node)
                    if active:
                        project_file.write('%s    Group {\n' % indent)
                        project_file.write('%s        name: "%s"\n' % (indent, env_name))
                        project_file.write(
                            '%s        condition: project.toolchain === "%s"\n' % (indent, env_name)
                        )
                        project_file.write('%s        files: [\n' % indent)
                        for node in active:
                            node_path = node.path_from(build_context.srcnode).replace('\\', '/')
                            project_file.write('%s            "%s",\n' % (indent, node_path))
                        project_file.write('%s        ]\n' % indent)
                        project_file.write('%s     }\n' % indent)
                project_file.write('%s}\n' % indent)


@build_framework.autosig_vars('includes', 'defines')
class qbs_toolchain(waflib.Task.Task):
    def run(self):
        with open(self.outputs[0].abspath(), 'w') as module:
            includes = getattr(self, 'includes')
            defines = getattr(self, 'defines')
            module.write(
                'Module {\n'
                '    property stringList includePaths: [\n')
            for include in includes:
                module.write('        "%s",\n' % (include.replace('\\', '/')))
            module.write(
                '    ]\n'
                '    property stringList defines: [\n')
            for define in defines:
                module.write('        "%s",\n' % (define.replace('"', '\\"')))
            module.write(
                '    ]\n'
                '}\n'
            )


class qbs_user(qtcreator_user):

    def sig_vars(self) -> None:
        qtcreator_user.sig_vars(self)
        self.m.update(inspect.getsource(self.make_build_configuration).encode())

    def make_build_configuration(
            self,
            build_configuration_index: int,
            bld_env: waflib.ConfigSet.ConfigSet,
            env: waflib.ConfigSet.ConfigSet,
            env_name: str,
            variant: str
    ) -> Tuple[str, List[Any]]:
        bld = self.generator.bld
        assert isinstance(bld, build_framework.BuildContext)
        assert bld.launcher is not None

        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, bld.srcnode.name)
        options = [a for a in sys.argv if a[0] == '-']
        extra_platform_flags = []
        if env.COMPILER_TARGET:
            extra_platform_flags.append(('modules.cpp.cxxFlags', "--target=%s" % env.COMPILER_TARGET))

        return (
            'ProjectExplorer.Target.BuildConfiguration.%d' % build_configuration_index, [
                (
                    'ProjectExplorer.BuildConfiguration.BuildDirectory',
                    bld.bldnode.make_node('qbs.build').abspath()
                ),
                (
                    'GenericProjectManager.GenericBuildConfiguration.BuildDirectory',
                    bld.bldnode.make_node('qbs.build').abspath()
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
                                        ('qbs.architecture', _qbs_arch(env.TARGET_ARCH)),
                                        ('qbs.targetPlatform', _qbs_platform(env)),
                                        ('projects.%s.toolchain' % appname, env_name),
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
                                    bld.srcnode.abspath()
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
                        ),
                        ('ProjectExplorer.BuildStepList.StepsCount', 2),
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
                                    bld.srcnode.abspath()
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
                        'TERM=msys',
                        'Python="%s"' % sys.executable,
                        'SrcDir="%s"' % bld.srcnode.abspath(),
                        'Variant=%s' % variant,
                        'PATH=%s' % os.environ['PATH']
                    )
                ), ('ProjectExplorer.ProjectConfiguration.DefaultDisplayName', 'Default'),
                ('ProjectExplorer.ProjectConfiguration.DisplayName', variant),
                ('ProjectExplorer.ProjectConfiguration.Id', 'Qbs.QbsBuildConfiguration'),
                ('Qbs.configName', '%s-%s' % (env_name, variant))
            ]
        )


class qcmake_user(qtcreator_user):

    def sig_vars(self) -> None:
        qtcreator_user.sig_vars(self)
        self.m.update(inspect.getsource(self.make_build_configuration).encode())

    def make_build_configuration(
            self,
            build_configuration_index: int,
            bld_env: waflib.ConfigSet.ConfigSet,
            env: waflib.ConfigSet.ConfigSet,
            env_name: str,
            variant: str
    ) -> Tuple[str, List[Any]]:
        bld = self.generator.bld
        assert isinstance(bld, build_framework.BuildContext)
        assert bld.launcher is not None
        options = [a for a in sys.argv if a[0] == '-']
        cmake_toolchains = getattr(self, 'cmake_toolchains')  # type: Dict[str, str]
        return (
            'ProjectExplorer.Target.BuildConfiguration.%d' % build_configuration_index, [
                ('CMake.Build.Type', variant),
                ('CMake.Configure.ClearSystemEnvironment', False),
                ('CMake.Configure.UserEnvironmentChanges', tuple()),
                ('CMake.Initial.Parameters',
                 '-DCMAKE_BUILD_TYPE:STRING=%(variant)s\n'
                 '-DCMAKE_TOOLCHAIN_FILE:STRING=%(toolchain)s\n'
                 '-DCMAKE_C_COMPILER:FILEPATH=%%{Compiler:Executable:C}\n'
                 '-DCMAKE_CXX_COMPILER:FILEPATH=%%{Compiler:Executable:Cxx}' % {
                     'variant': variant,
                     'toolchain': cmake_toolchains[env_name],
                 }),
                (
                    'ProjectExplorer.BuildConfiguration.BuildDirectory',
                    bld.bldnode.make_node('qcmake.build/%s/%s' % (env_name, variant)).abspath()
                ),
                (
                    'GenericProjectManager.GenericBuildConfiguration.BuildDirectory',
                    bld.bldnode.make_node('qcmake.build/%s/%s' % (env_name, variant)).abspath()
                ),
                (
                    'ProjectExplorer.BuildConfiguration.BuildStepList.0', [
                        (
                            'ProjectExplorer.BuildStepList.Step.0', [
                                ('CMakeProjectManager.MakeStep.BuildPreset', ''),
                                ('CMakeProjectManager.MakeStep.BuildTargets', ('all',)),
                                ('CMakeProjectManager.MakeStep.ClearSystemEnvironment', False),
                                ('CMakeProjectManager.MakeStep.UserEnvironmentChanges', tuple()),
                                ('ProjectExplorer.BuildStep.Enabled', False),
                                ('ProjectExplorer.ProjectConfiguration.DisplayName', 'Build'),
                                ('ProjectExplorer.ProjectConfiguration.Id', 'CMakeProjectManager.MakeStep')
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
                                    bld.srcnode.abspath()
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
                        ),
                        ('ProjectExplorer.BuildStepList.StepsCount', 2),
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
                                    bld.srcnode.abspath()
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
                        'TERM=msys',
                        'Python="%s"' % sys.executable,
                        'SrcDir="%s"' % bld.srcnode.abspath(),
                        'Variant=%s' % variant,
                        'PATH=%s' % os.environ['PATH'],
                        'CMAKE_C_COMPILER_LAUNCHER:STRING=%s;%s/mak/bin/true.py;--' % (
                            sys.executable.replace('\\', '/'),
                            bld.motornode.abspath().replace('\\', '/')),
                        'CMAKE_CXX_COMPILER_LAUNCHER:STRING=%s;%s/mak/bin/true.py;--' % (
                            sys.executable.replace('\\', '/'),
                            bld.motornode.abspath().replace('\\', '/')),
                        'CMAKE_C_LINKER_LAUNCHER:STRING=%s;%s/mak/bin/true.py;--' % (
                            sys.executable.replace('\\', '/'),
                            bld.motornode.abspath().replace('\\', '/')),
                        'CMAKE_CXX_LINKER_LAUNCHER:STRING=%s;%s/mak/bin/true.py;--' % (
                            sys.executable.replace('\\', '/'),
                            bld.motornode.abspath().replace('\\', '/')),
                    )
                ), ('ProjectExplorer.ProjectConfiguration.DefaultDisplayName', 'Default'),
                ('ProjectExplorer.ProjectConfiguration.DisplayName', variant),
                ('ProjectExplorer.ProjectConfiguration.Id', 'CMakeProjectManager.CMakeBuildConfiguration')
            ]
        )


@waflib.TaskGen.feature('motor:qtcreator')
def create_qtcreator_configs(task_gen: waflib.TaskGen.task_gen) -> None:
    task_gen.create_task('qtcreator_codestyle', [], [])
    profiles = build_framework.make_bld_node(task_gen, 'config', '..', 'profiles.xml')
    profiles.parent.mkdir()
    debuggers = build_framework.make_bld_node(task_gen, 'config', '..', 'debuggers.xml')
    cmaketools = build_framework.make_bld_node(task_gen, 'config', '..', 'cmaketools.xml')
    toolchains = build_framework.make_bld_node(task_gen, 'config', '..', 'toolchains.xml')
    task_gen.create_task('qtcreator_config', [], [profiles, debuggers, cmaketools, toolchains])
    task_gen.create_task('qtcreator_ini', [], [])
    build_framework.install_files(task_gen, HOME_DIRECTORY, [profiles, debuggers, cmaketools, toolchains])


@waflib.TaskGen.feature('motor:qbs')
def create_qbs(task_gen: waflib.TaskGen.task_gen) -> None:
    appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, task_gen.bld.srcnode.name)
    projects = {}  # type: _ProjectMap
    project_list = []
    for group in task_gen.bld.groups:
        for task_gen in group:
            if 'motor:c' not in task_gen.features and 'motor:cxx' not in task_gen.features:
                continue
            name = getattr(task_gen, 'project_name').split('.')
            p = projects
            for c in name[:-1]:
                try:
                    p_sub, _ = p[c]
                except KeyError:
                    p_sub = {}
                    p[c] = p_sub, None
                p = p_sub
            try:
                p_sub, tg = p[name[-1]]
            except KeyError:
                p[name[-1]] = {}, task_gen
            else:
                assert tg is None
                p[name[-1]] = p_sub, task_gen
            project_list.append(task_gen)

    qbs_file = build_framework.make_bld_node(task_gen, None, None, appname + '.qbs')
    qbs_user_file = build_framework.make_bld_node(task_gen, None, None, appname + '.qbs.user')
    qbs_file.parent.mkdir()
    task_gen.create_task('qbs', [], [qbs_file], projects=projects)
    task_gen.create_task('qbs_user', [], [qbs_user_file])
    for toolchain in task_gen.bld.env.ALL_TOOLCHAINS:
        env = task_gen.bld.all_envs[toolchain]
        if env.SUB_TOOLCHAINS:
            env = task_gen.bld.all_envs[env.SUB_TOOLCHAINS[0]]
        toolchain_file = build_framework.make_bld_node(task_gen, toolchain, 'modules/motor_module', 'MotorModule.qbs')
        toolchain_file.parent.mkdir()
        task_gen.create_task('qbs_toolchain', [], [toolchain_file], includes=env.INCLUDES, defines=env.DEFINES)
    build_framework.install_files(task_gen, task_gen.bld.srcnode.abspath(), [qbs_file, qbs_user_file])


@waflib.TaskGen.feature('motor:qcmake')
def create_qcmake(task_gen: waflib.TaskGen.task_gen) -> None:
    configurations = getattr(task_gen.bld, 'motor_cmake_tg').toolchains  # type: List[Tuple[str, waflib.Node.Node]]
    cmake_toolchains = {}
    for toolchain, node in configurations:
        cmake_toolchains[toolchain] = node.abspath()
    qcmake_user_file = build_framework.make_bld_node(task_gen, None, None, 'CMakeLists.txt.user')
    qcmake_user_file.parent.mkdir()
    task_gen.create_task('qcmake_user', [], [qcmake_user_file],
                         cmake_toolchains=cmake_toolchains)
    build_framework.install_files(task_gen, task_gen.bld.srcnode.abspath(), [qcmake_user_file])


def build(build_context: build_framework.BuildContext) -> None:
    if 'qtcreator' in build_context.env.PROJECTS:
        build_context(
            group='qtcreator',
            features=['motor:qtcreator'],
            target='qtcreator',
            use=[]
        )
    if 'qbs' in build_context.env.PROJECTS:
        build_context(
            group='qbs',
            features=['motor:qbs'],
            target='qbs',
            use=[]
        )
    if 'qcmake' in build_context.env.PROJECTS:
        build_context(
            group='qcmake',
            features=['motor:qcmake'],
            target='qcmake',
            use=[]
        )
