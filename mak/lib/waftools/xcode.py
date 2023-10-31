import os
import sys
import xml.dom.minidom
import build_framework
import waflib.Context
import waflib.Errors
import waflib.Node
import waflib.TaskGen
from typing import Any, Dict, IO, List, Optional, Tuple, TypeVar, Union

x = 2000
y = 10500999


def new_xcode_id() -> str:
    global x, y
    y = y + 1
    return "%04X%04X%04X%012d" % (0, x, 0, y)


class XmlNode(object):

    def __init__(self) -> None:
        self.document = xml.dom.minidom.Document()
        self.document.encoding = 'UTF-8'

    def _add(
            self,
            node: xml.dom.minidom.Node,
            child_node: str,
            value: Union[None, str, Dict[str, str]] = None
    ) -> xml.dom.minidom.Element:

        def set_attributes(n: xml.dom.minidom.Element, attrs: Dict[str, str]) -> None:
            for k, v in attrs.items():
                n.setAttribute(k, v)

        el = self.document.createElement(child_node)
        if value is not None:
            if isinstance(value, str):
                el.appendChild(self.document.createTextNode(value))
            elif isinstance(value, dict):
                set_attributes(el, value)
        node.appendChild(el)
        return el

    def write(self, node: waflib.Node.Node) -> None:
        node.write(self.document.toxml())


class XCodeScheme(XmlNode):

    def __init__(
            self,
            identifier: str,
            name: str,
            product: str,
            project: str,
            dummy: bool
    ) -> None:
        XmlNode.__init__(self)
        self.id = identifier
        self.name = name
        self.dummy = dummy
        scheme = self._add(self.document, 'Scheme', {'LastUpgradeVersion': '0450', 'version': '1.3'})
        build_action = self._add(
            scheme, 'BuildAction', {
                'parallelizeBuildables': 'YES',
                'buildImplicitDependencies': 'YES'
            }
        )
        build_action_entries = self._add(build_action, 'BuildActionEntries')
        if not dummy:
            build_action_entry = self._add(
                build_action_entries, 'BuildActionEntry', {
                    'buildForTesting': 'YES',
                    'buildForRunning': 'YES',
                    'buildForProfiling': 'YES',
                    'buildForArchiving': 'YES',
                    'buildForAnalyzing': 'YES'
                }
            )
            test_action = self._add(
                scheme, 'TestAction', {
                    'selectedDebuggerIdentifier': 'Xcode.DebuggerFoundation.Debugger.LLDB',
                    'selectedLaunchIdentifier': 'Xcode.DebuggerFoundation.Debugger.LLDB',
                    'shouldUseLaunchSchemeArgsEnv': 'YES',
                    'buildConfiguration': 'debug'
                }
            )
            self._add(test_action, 'Testables')
            macro_expansion = self._add(test_action, 'MacroExpansion')
            launch_action = self._add(
                scheme, 'LaunchAction', {
                    'selectedDebuggerIdentifier': 'Xcode.DebuggerFoundation.Debugger.LLDB',
                    'selectedLaunchIdentifier': 'Xcode.DebuggerFoundation.Debugger.LLDB',
                    'launchStyle': '0',
                    'useCustomWorkingDirectory': 'NO',
                    'buildConfiguration': 'debug',
                    'ignoresPersistentStateOnLaunch': 'NO',
                    'debugDocumentVersioning': 'NO',
                    'allowLocationSimulation': 'YES'
                }
            )
            buildable_product_runnable = self._add(launch_action, 'BuildableProductRunnable')
            self._add(launch_action, 'AdditionalOptions')
            profile_action = self._add(
                scheme, 'ProfileAction', {
                    'buildConfiguration': 'profile',
                    'shouldUseLaunchSchemeArgsEnv': 'YES',
                    'savedToolIdentifier': '',
                    'useCustomWorkingDirectory': 'NO',
                    'debugDocumentVersioning': 'NO'
                }
            )
            buildable_product_runnable2 = self._add(profile_action, 'BuildableProductRunnable')
            self._add(scheme, 'AnalyzeAction', {'buildConfiguration': 'debug'})
            self._add(
                scheme, 'ArchiveAction', {
                    'buildConfiguration': 'final',
                    'revealArchiveInOrganizer': 'YES'
                }
            )
            for node in [build_action_entry, macro_expansion, buildable_product_runnable, buildable_product_runnable2]:
                self._add(
                    node, 'BuildableReference', {
                        'BuildableIdentifier': 'primary',
                        'BlueprintIdentifier': self.id,
                        'BuildableName': product,
                        'BlueprintName': name,
                        'ReferencedContainer': 'container:%s' % project
                    }
                )
        else:
            build_action_entry = self._add(
                build_action_entries, 'BuildActionEntry', {
                    'buildForTesting': 'NO',
                    'buildForRunning': 'NO',
                    'buildForProfiling': 'NO',
                    'buildForArchiving': 'NO',
                    'buildForAnalyzinf': 'NO'
                }
            )
            self._add(
                build_action_entry, 'BuildableReference', {
                    'BuildableIdentifier': 'primary',
                    'BlueprintIdentifier': self.id,
                    'BuildableName': product,
                    'BlueprintName': name,
                    'ReferencedContainer': 'container:%s' % project
                }
            )


class XCodeSchemeList(XmlNode):

    def __init__(self) -> None:
        XmlNode.__init__(self)
        plist = self._add(self.document, 'plist', {'version': '1.0'})
        dict_value = self._add(plist, 'dict')
        self._add(dict_value, 'key', 'SchemeUserState')
        self.userstates = self._add(dict_value, 'dict')
        self._add(dict_value, 'key', 'SuppressBuildableAutocreation')
        self.autocreation = self._add(dict_value, 'dict')
        self.order = 0

    def add(self, scheme: XCodeScheme) -> None:
        self._add(self.userstates, 'key', '%s.xcscheme' % scheme.name)
        dict_value = self._add(self.userstates, 'dict')
        self._add(dict_value, 'key', 'isShown')
        if scheme.dummy:
            self._add(dict_value, 'false')
        else:
            self._add(dict_value, 'true')
        self._add(dict_value, 'key', 'orderHint')
        self._add(dict_value, 'integer', self.order.__str__())
        self._add(self.autocreation, 'key', scheme.id)
        dict_value = self._add(self.autocreation, 'dict')
        self._add(dict_value, 'key', 'primary')
        self._add(dict_value, 'true')
        self.order = self.order + 1


class XCodeNode(object):

    def __init__(self) -> None:
        self._id = new_xcode_id()

    def tostring(self, value: Any) -> str:
        if isinstance(value, dict):
            result = "{\n"
            for k, v in value.items():
                result = result + "\t\t\t%s = %s;\n" % (k, self.tostring(v))
            result = result + "\t\t}"
            return result
        elif isinstance(value, str):
            return "\"%s\"" % value.replace('"', '\\"')
        elif isinstance(value, list):
            result = "(\n"
            for i in value:
                result = result + "\t\t\t%s,\n" % self.tostring(i)
            result = result + "\t\t)"
            return result
        elif isinstance(value, XCodeNode):
            return value._id
        else:
            return str(value)

    def write_recursive(self, value: Any, file: IO[str]) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                self.write_recursive(v, file)
        elif isinstance(value, list):
            for i in value:
                self.write_recursive(i, file)
        elif isinstance(value, XCodeNode):
            value.write(file)

    def write(self, file: IO[str]) -> None:
        for attribute, value in self.__dict__.items():
            if attribute[0] != '_':
                self.write_recursive(value, file)

        w = file.write
        w("\t%s = {\n" % self._id)
        w("\t\tisa = %s;\n" % self.__class__.__name__)
        for attribute, value in self.__dict__.items():
            if attribute[0] != '_':
                w("\t\t%s = %s;\n" % (attribute, self.tostring(value)))
        w("\t};\n\n")


# Configurations
class XCBuildConfiguration(XCodeNode):

    def __init__(self, name: str, settings: Optional[Dict[str, Union[str, List[str]]]] = None) -> None:
        XCodeNode.__init__(self)
        self.baseConfigurationReference = ""
        self.buildSettings = settings or {}
        self.name = name


class XCConfigurationList(XCodeNode):

    def __init__(self, settings: List[XCBuildConfiguration]) -> None:
        XCodeNode.__init__(self)
        self.buildConfigurations = settings
        self.defaultConfigurationIsVisible = 0
        self.defaultConfigurationName = settings and settings[0].name or ""


# Group/Files
class PBXFileReference(XCodeNode):
    sort_prefix = 'b'

    def __init__(self, name: str, path: str, filetype: str = '', sourcetree: str = "SOURCE_ROOT") -> None:
        XCodeNode.__init__(self)
        self.fileEncoding = 4
        self._parse = False
        if not filetype:
            _, ext = os.path.splitext(name)
            if ext == '.h':
                filetype = "sourcecode.c.h"
            elif ext in ['.hh', '.inl', '.hpp']:
                filetype = "sourcecode.cpp.h"
                self.xcLanguageSpecificationIdentifier = "xcode.lang.cpp"
            elif ext == '.c':
                filetype = "sourcecode.c.c"
            elif ext == '.m':
                filetype = "sourcecode.c.objc"
            elif ext == '.mm':
                filetype = "sourcecode.cpp.objcpp"
            elif ext in ['.cc', '.cpp', '.C', '.cxx', '.c++']:
                filetype = "sourcecode.cpp.cpp"
            elif ext in ['.l', '.ll']:
                filetype = "sourcecode.lex"
            elif ext in ['.y', '.yy']:
                filetype = "sourcecode.yacc"
            elif ext == '.plist':
                filetype = "text.plist.xml"
            elif ext == ".nib":
                filetype = "wrapper.nib"
            elif ext == ".xib":
                filetype = "text.xib"
            elif name == 'wscript' or ext == '.py':
                filetype = "sourcecode.script.python"
                self.xcLanguageSpecificationIdentifier = "xcode.lang.python"
            else:
                filetype = "text"
        self.lastKnownFileType = filetype
        self.name = name
        self.path = path
        self.sourceTree = sourcetree


class PBXGroup(XCodeNode):
    sort_prefix = 'a'

    def __init__(self, name: str, sourcetree: str = "<group>"):
        XCodeNode.__init__(self)
        self.children = []  # type: List[Union["PBXGroup", PBXFileReference]]
        self.name = name
        self.sourceTree = sourcetree
        self._groups = {}  # type: Dict[str, "PBXGroup"]

    def add_group(self, group: "PBXGroup") -> "PBXGroup":
        self._groups[group.name] = group
        self.children.append(group)
        self.sort()
        return group

    def add(self, root_node: waflib.Node.Node, source_node: waflib.Node.Node) -> List[PBXFileReference]:
        result = []  # type: List[PBXFileReference]
        try:
            file_list = source_node.listdir()
        except OSError:
            pass
        else:
            for f in file_list:
                fullname = os.path.join(source_node.abspath(), f)
                if os.path.isdir(fullname):
                    try:
                        g = self[f]
                        assert isinstance(g, PBXGroup)
                    except KeyError:
                        g = self.add_group(PBXGroup(f))
                    result += g.add(root_node, source_node.make_node(f))
                else:
                    f_ref = PBXFileReference(f, os.path.join(source_node.path_from(root_node), f))
                    self.children.append(f_ref)
                    result.append(f_ref)
            self.sort()
        return result

    def sort(self) -> None:
        self.children.sort(key=lambda elem: elem.__class__.sort_prefix + elem.name)

    def __getitem__(self, name: str) -> "PBXGroup":
        return self._groups[name]


class PBXBuildFile(XCodeNode):

    def __init__(self, file: PBXFileReference) -> None:
        XCodeNode.__init__(self)
        self.fileRef = file


# Targets
class PBXLegacyTarget(XCodeNode):

    def __init__(self, action: str, target: str = '') -> None:
        XCodeNode.__init__(self)
        self.buildConfigurationList = XCConfigurationList(
            [
                XCBuildConfiguration('debug', {}),
                XCBuildConfiguration('profile', {}),
                XCBuildConfiguration('final', {}),
            ]
        )
        self.buildArgumentsString = "%s %s" % (sys.argv[0], action)
        self.buildPhases = []  # type: List[_PBXBuildPhase]
        self.buildToolPath = sys.executable
        self.buildWorkingDirectory = ""
        self.dependencies = []  # type: List[PBXLegacyTarget]
        self.name = action
        self.productName = target or action
        self.passBuildSettingsInEnvironment = 0


class _PBXBuildPhase(XCodeNode):

    def __init__(self) -> None:
        XCodeNode.__init__(self)
        self.buildActionMask = 2147483647
        self.files = []  # type: List[PBXBuildFile]


class PBXShellScriptBuildPhase(_PBXBuildPhase):

    def __init__(self, action: str) -> None:
        _PBXBuildPhase.__init__(self)
        self.inputPaths = []  # type: List[None]
        self.outputPaths = []  # type: List[None]
        self.runOnlyForDeploymentPostProcessing = 0
        self.shellPath = "/bin/sh"
        self.shellScript = "%s %s %s" % (sys.executable, sys.argv[0], action)


class PBXSourcesBuildPhase(_PBXBuildPhase):

    def __init__(self, files: List[PBXFileReference]) -> None:
        _PBXBuildPhase.__init__(self)
        self.runOnlyForDeploymentPostProcessing = 0
        self.files = [PBXBuildFile(file) for file in files]


class PBXFrameworksBuildPhase(PBXSourcesBuildPhase):

    def __init__(self, frameworks: List[PBXFileReference]) -> None:
        PBXSourcesBuildPhase.__init__(self, frameworks)


class PBXNativeTarget(XCodeNode):

    def __init__(
            self,
            name: str,
            product: PBXFileReference,
            product_type: str,
            build: List[_PBXBuildPhase],
            configs: List[XCBuildConfiguration]
    ) -> None:
        XCodeNode.__init__(self)
        self.buildConfigurationList = XCConfigurationList(configs)
        self.buildPhases = build
        self.buildRules = []  # type: List[None]
        self.dependencies = []  # type: List[None]
        self.name = name
        self.productName = name
        self.productType = product_type
        self.productReference = product


# Root project object

T = TypeVar('T', str, List[str])


def macarch(arch: T) -> T:
    arch_map = {
        'amd64': 'x86_64',
        'arm': 'armv6',
        'armv7a': 'armv7',
        'x86': 'i386',
        'i486': 'i386',
        'i586': 'i386',
        'i686': 'i386',
        'powerpc64': 'ppc64',
        'powerpc': 'ppc'
    }
    if isinstance(arch, list):
        return [macarch(a) for a in arch]
    else:
        return arch_map.get(arch, arch)


class PBXProject(XCodeNode):

    def __init__(self, name: str, version: Tuple[str, int], builder: build_framework.BuildContext) -> None:
        XCodeNode.__init__(self)
        self.buildConfigurationList = XCConfigurationList(
            [
                XCBuildConfiguration('debug', {
                    'BUILT_OUTPUTS_DIR': 'build',
                    'CONFIG': 'debug'
                }),
                XCBuildConfiguration('profile', {
                    'BUILT_OUTPUTS_DIR': 'build',
                    'CONFIG': 'profile'
                }),
                XCBuildConfiguration('final', {
                    'BUILT_OUTPUTS_DIR': 'build',
                    'CONFIG': 'final'
                }),
            ]
        )
        self.compatibilityVersion = version[0]
        self.hasScannedForEncodings = 1
        self.mainGroup = PBXGroup(name)
        self._mainGroup = PBXGroup(name)
        self.mainGroup.children.append(self._mainGroup)
        self.projectRoot = ""
        self.projectDirPath = ""
        self.targets = []  # type: List[Union[PBXNativeTarget, PBXLegacyTarget]]
        self._objectVersion = version[1]
        self._output = PBXGroup('Products')
        self._output2 = PBXGroup('Dummies')
        self.mainGroup.children.append(self._output)
        self._output.children.append(self._output2)
        self._frameworks = PBXGroup('Frameworks')
        self.mainGroup.children.append(self._frameworks)
        self._frameworks_seen = {}  # type: Dict[str, Tuple[List[str], PBXGroup]]
        self._frameworks_files = []
        for env_name in builder.env.ALL_TOOLCHAINS:
            env = builder.all_envs[env_name]
            if env.XCODE_FRAMEWORKS:
                try:
                    seen, group = self._frameworks_seen[env.MACOSX_SDK]
                except KeyError:
                    seen = []
                    group = PBXGroup(env.MACOSX_SDK)
                    self._frameworks.children.append(group)
                    self._frameworks_seen[env.MACOSX_SDK] = (seen, group)
                for f in env.XCODE_FRAMEWORKS:
                    if f not in seen:
                        seen.append(f)
                        file = PBXFileReference(
                            '%s.framework' % f,
                            os.path.join(env.XCODE_SDK_PATH, 'System', 'Library', 'Frameworks', '%s.framework' % f),
                            'wrapper.framework', '<absolute>'
                        )
                        self._frameworks_files.append(file)
                        group.children.append(file)

    def write(self, file: IO[str]) -> None:
        w = file.write
        w("// !$*UTF8*$!\n")
        w("{\n")
        w("\tarchiveVersion = 1;\n")
        w("\tclasses = {\n")
        w("\t};\n")
        w("\tobjectVersion = %d;\n" % self._objectVersion)
        w("\tobjects = {\n\n")

        XCodeNode.write(self, file)

        w("\t};\n")
        w("\trootObject = %s;\n" % self._id)
        w("}\n")

    def add(
            self,
            bld: build_framework.BuildContext,
            p: waflib.TaskGen.task_gen,
            schemes: waflib.Node.Node,
            schememanagement: XCodeSchemeList,
            project_name: str
    ) -> str:

        def get_include_path(i: Union[str, waflib.Node.Node]) -> str:
            if isinstance(i, str):
                return '$(SOURCE_ROOT)/' + i
            else:
                return '$(SOURCE_ROOT)/' + i.path_from(bld.srcnode)

        names = p.target.split('.')
        sources = []
        if 'motor:kernel' not in p.features:
            group = self._mainGroup
            for name in names:
                try:
                    group = group[name]
                except KeyError:
                    group = group.add_group(PBXGroup(name))

            source_nodes = getattr(p, 'source_nodes', [])
            for _, source_node in source_nodes:
                sources += group.add(bld.path, source_node)

        includes = set(getattr(p, 'includes', []))
        defines = set(getattr(p, 'defines', []))
        task_gens = getattr(p, 'use', [])[:]
        seen = set([])
        while task_gens:
            name = task_gens.pop()
            if name not in seen:
                try:
                    task_gen = bld.get_tgen_by_name(name)
                except waflib.Errors.WafError:
                    continue
                seen.add(name)
                task_gens += getattr(task_gen, 'use', [])
                includes.union(getattr(task_gen, 'export_includes', []))
                includes.union(getattr(task_gen, 'export_system_includes', []))
                defines.union(getattr(task_gen, 'export_defines', []))

        for toolchain in bld.env.ALL_TOOLCHAINS:
            env = bld.all_envs[toolchain]
            includes.union(env.INCLUDES)
            defines.union(env.DEFINES)
        variants = []
        for variant in bld.env.ALL_VARIANTS:
            variants.append(
                XCBuildConfiguration(
                    variant, {
                        'PRODUCT_NAME': p.target,
                        'ARCHS': ['x86_64'],
                        'VALID_ARCHS': ['x86_64'],
                        'SDKROOT': 'macosx',
                        'SUPPORTED_PLATFORMS': 'macosx',
                        'HEADER_SEARCH_PATHS': [get_include_path(i) for i in includes],
                        'GCC_PREPROCESSOR_DEFINITIONS': [d for d in defines]
                    }
                )
            )
        build_phase = PBXSourcesBuildPhase(sources)
        framework_phase = PBXFrameworksBuildPhase(self._frameworks_files)
        target = PBXNativeTarget(
            'index.' + p.target, PBXFileReference(p.target, 'lib%s.a' % p.target, 'archive.ar', 'BUILT_PRODUCTS_DIR'),
            "com.apple.product-type.library.static", [build_phase, framework_phase], variants
        )
        self._output2.children.append(target.productReference)
        self.targets.append(target)
        scheme = XCodeScheme(target._id, 'index.' + p.target, 'lib%s.a' % p.target, project_name, True)
        scheme.write(schemes.make_node('index.%s.xcscheme' % p.target))
        schememanagement.add(scheme)
        return 'index.%s.xcscheme' % p.target


class xcode(build_framework.BuildContext):
    """creates projects for XCode 3.x and 4.x"""
    cmd = 'xcode'
    fun = 'build'
    optim = 'debug'
    version = ('Xcode 3.1', 45)
    motor_toolchain = 'projects'
    motor_variant = 'projects.setup'
    variant = 'projects/xcode'

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
        self.env.TOOLCHAIN = '$(TOOLCHAIN)'
        self.env.VARIANT = '$(CONFIG)'
        self.env.PREFIX = '$(PREFIX)'
        self.env.DEPLOY_ROOTDIR = '$(DEPLOY_ROOTDIR)'
        self.env.DEPLOY_BINDIR = '$(DEPLOY_BINDIR)'
        self.env.DEPLOY_RUNBINDIR = '$(DEPLOY_RUNBINDIR)'
        self.env.DEPLOY_LIBDIR = '$(DEPLOY_LIBDIR)'
        self.env.DEPLOY_INCLUDEDIR = '$(DEPLOY_INCLUDEDIR)'
        self.env.DEPLOY_DATADIR = '$(DEPLOY_DATADIR)'
        self.env.DEPLOY_PLUGINDIR = '$(DEPLOY_PLUGINDIR)'
        self.env.DEPLOY_KERNELDIR = '$(DEPLOY_KERNELDIR)'
        build_framework.add_feature(self, 'GUI')
        self.recurse([self.run_dir])
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, os.path.basename(self.srcnode.abspath()))
        import getpass

        project = self.srcnode.make_node('%s.%s.xcodeproj' % (appname, self.__class__.cmd))
        project.mkdir()
        userdata = project.make_node('xcuserdata')
        userdata.mkdir()
        userdata = userdata.make_node('%s.xcuserdatad' % getpass.getuser())
        userdata.mkdir()
        schemes = userdata.make_node('xcschemes')
        schemes.mkdir()
        p = PBXProject(appname, self.__class__.version, self)

        valid_schemes = set([])
        schememanagement = XCodeSchemeList()
        for g in self.groups:
            for tg in g:
                if not isinstance(tg, waflib.TaskGen.task_gen):
                    continue
                tg.post()
                valid_schemes.add(p.add(self, tg, schemes, schememanagement, project.name))

        for toolchain in self.env.ALL_TOOLCHAINS:
            env = self.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                bld_env = self.all_envs[env.SUB_TOOLCHAINS[0]]
                all_envs = [self.all_envs[t] for t in env.SUB_TOOLCHAINS]
            else:
                bld_env = env
                all_envs = [env]
            if bld_env.XCODE_ABI == 'mach_o':
                variants = []
                for variant in self.env.ALL_VARIANTS:
                    variants.append(
                        XCBuildConfiguration(
                            variant, {
                                'PRODUCT_NAME':
                                    appname,
                                'BUILT_PRODUCTS_DIR':
                                    os.path.join(env.PREFIX, variant),
                                'CONFIGURATION_BUILD_DIR':
                                    os.path.join(env.PREFIX, variant),
                                'ARCHS':
                                    ' '.join([macarch(e.VALID_ARCHITECTURES[0]) for e in all_envs]),
                                'VALID_ARCHS':
                                    ' '.join([macarch(e.VALID_ARCHITECTURES[0]) for e in all_envs]),
                                'SDKROOT':
                                    bld_env.XCODE_SDKROOT,
                                '%s_DEPLOYMENT_TARGET' % bld_env.XCODE_SUPPORTEDPLATFORMS.upper():
                                    bld_env.MACOSX_SDK_MIN,
                                'SUPPORTED_PLATFORMS':
                                    bld_env.XCODE_SUPPORTEDPLATFORMS
                            }
                        )
                    )
                build = PBXShellScriptBuildPhase('build:' + toolchain + ':${CONFIG} --werror')
                target = PBXNativeTarget(
                    toolchain, PBXFileReference(appname, appname + '.app', 'wrapper.application', 'BUILT_PRODUCTS_DIR'),
                    "com.apple.product-type.application", [build], variants
                )
                p.targets.append(target)
                getattr(p, '_output').children.append(target.productReference)
                scheme = XCodeScheme(getattr(target, '_id'), toolchain, appname + '.app', project.name, False)
            else:
                legacy_target = PBXLegacyTarget('build:%s:$(CONFIG) --werror' % toolchain, toolchain)
                p.targets.append(legacy_target)
                scheme = XCodeScheme(getattr(legacy_target, '_id'), toolchain, appname, project.name, False)
            scheme.write(schemes.make_node('%s.xcscheme' % toolchain))
            schememanagement.add(scheme)
            valid_schemes.add('%s.xcscheme' % toolchain)
        for n in schemes.listdir():
            if n not in valid_schemes:
                schemes.make_node(n).delete()

        schememanagement.write(schemes.make_node('xcschememanagement.plist'))
        node = project.make_node('project.pbxproj')
        p.write(open(node.abspath(), 'w'))
        return None


class xcode5(xcode):
    """creates projects for XCode version 5.x"""
    cmd = 'xcode5'
    fun = 'build'
    optim = 'debug'
    version = ('Xcode 3.2', 46)
