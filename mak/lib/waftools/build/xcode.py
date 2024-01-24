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


def _new_xcode_id() -> str:
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


class XCodeNode(object):

    def __init__(self, identifier: Optional[str] = None) -> None:
        if identifier is None:
            identifier = _new_xcode_id()
        self._id = identifier

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

    def __init__(self, name: str, source_tree: str = "<group>"):
        XCodeNode.__init__(self)
        self.children = []  # type: List[Union["PBXGroup", PBXFileReference]]
        self.name = name
        self.sourceTree = source_tree
        self._groups = {}  # type: Dict[str, "PBXGroup"]

    def add_group(self, group: "PBXGroup") -> "PBXGroup":
        self._groups[group.name] = group
        self.children.append(group)
        self.sort()
        return group

    def add(self, root_node: waflib.Node.Node, source_node: waflib.Node.Node) -> List[PBXFileReference]:
        result = []  # type: List[PBXFileReference]

        if source_node.isdir():
            all_sub_nodes = source_node.ant_glob('**/*', excl=['kernels/**', 'tests/**', '**/*.pyc'], remove=False)
        else:
            all_sub_nodes = [source_node]
            source_node = source_node.parent

        def get_group(node: waflib.Node.Node) -> PBXGroup:
            if node == source_node:
                return self
            else:
                parent_group = get_group(node.parent)
                try:
                    g = parent_group[node.name]
                except KeyError:
                    g = parent_group.add_group(PBXGroup(node.name))
                return g

        for file in all_sub_nodes:
            f = file.name
            group = get_group(file.parent)
            f_ref = PBXFileReference(f, file.path_from(root_node))
            group.children.append(f_ref)
            result.append(f_ref)
            group.sort()
        return result

    def sort(self) -> None:
        self.children.sort(key=lambda elem: elem.__class__.sort_prefix + elem.name)

    def __getitem__(self, name: str) -> "PBXGroup":
        return self._groups[name]


class PBXBuildFile(XCodeNode):

    def __init__(self, file: PBXFileReference) -> None:
        XCodeNode.__init__(self)
        self.fileRef = file


class PBXLegacyTarget(XCodeNode):

    def __init__(self, identifier: str, action: str, target: str, bldnode: waflib.Node.Node) -> None:
        XCodeNode.__init__(self, identifier)
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
        self.buildWorkingDirectory = bldnode.abspath()
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
        self.alwaysOutOfDate = 1
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
            self, identifier: str, name: str, product: PBXFileReference, product_type: str, build: List[_PBXBuildPhase],
            configs: List[XCBuildConfiguration]
    ) -> None:
        XCodeNode.__init__(self, identifier)
        self.buildConfigurationList = XCConfigurationList(configs)
        self.buildPhases = build
        self.buildRules = []  # type: List[None]
        self.dependencies = []  # type: List[None]
        self.name = name
        self.productName = name
        self.productType = product_type
        self.productReference = product


T = TypeVar('T', str, List[str])


def _macarch(arch: T) -> T:
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
        return [_macarch(a) for a in arch]
    else:
        return arch_map.get(arch, arch)


class PBXProject(XCodeNode):

    def __init__(self, name: str, version: Tuple[str, int], builder: build_framework.ProjectGenerator) -> None:
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
            legacy_target_id: str,
            target: str,
            target_includes: List[waflib.Node.Node],
            defines: List[str],
            source_nodes: List[Tuple[str, waflib.Node.Node]],
            srcnode: waflib.Node.Node,
            variant_names: List[str]
    ) -> None:
        names = target.split('.')
        sources = []
        group = self._mainGroup
        for name in names:
            try:
                group = group[name]
            except KeyError:
                group = group.add_group(PBXGroup(name))

        for name, source_node in source_nodes:
            if name:
                try:
                    g = group[name]
                except KeyError:
                    g = group.add_group(PBXGroup(name))
            else:
                g = group
            sources += g.add(srcnode, source_node)

        variants = []
        for variant in variant_names:
            variants.append(
                XCBuildConfiguration(
                    variant, {
                        'PRODUCT_NAME': target,
                        'ARCHS': ['x86_64'],
                        'VALID_ARCHS': ['x86_64'],
                        'SDKROOT': 'macosx',
                        'SUPPORTED_PLATFORMS': 'macosx',
                        'HEADER_SEARCH_PATHS': ['$(SOURCE_ROOT)/' + i.path_from(srcnode) for i in target_includes],
                        'GCC_PREPROCESSOR_DEFINITIONS': [d for d in defines]
                    }
                )
            )
        build_phase = PBXSourcesBuildPhase(sources)
        framework_phase = PBXFrameworksBuildPhase(self._frameworks_files)
        native_target = PBXNativeTarget(
            legacy_target_id,
            'index.' + target,
            PBXFileReference(target, 'lib%s.a' % target, 'archive.ar', 'BUILT_PRODUCTS_DIR'),
            "com.apple.product-type.library.static",
            [build_phase, framework_phase],
            variants
        )
        self._output2.children.append(native_target.productReference)
        self.targets.append(native_target)


@build_framework.autosig_vars('identifier', 'scheme_name', 'product', 'project', 'dummy')
class xcode_scheme(waflib.Task.Task):
    def run(self) -> Optional[int]:
        identifier = getattr(self, 'identifier')  # type: str
        name = getattr(self, 'scheme_name')  # type: str
        product = getattr(self, 'product')  # type: str
        project = getattr(self, 'project')  # type: str
        dummy = getattr(self, 'dummy')  # type: bool

        node = XmlNode()
        scheme = node._add(node.document, 'Scheme', {'LastUpgradeVersion': '0450', 'version': '1.3'})
        build_action = node._add(
            scheme, 'BuildAction', {
                'parallelizeBuildables': 'YES',
                'buildImplicitDependencies': 'YES'
            }
        )
        build_action_entries = node._add(build_action, 'BuildActionEntries')
        if not dummy:
            build_action_entry = node._add(
                build_action_entries, 'BuildActionEntry', {
                    'buildForTesting': 'YES',
                    'buildForRunning': 'YES',
                    'buildForProfiling': 'YES',
                    'buildForArchiving': 'YES',
                    'buildForAnalyzing': 'YES'
                }
            )
            test_action = node._add(
                scheme, 'TestAction', {
                    'selectedDebuggerIdentifier': 'Xcode.DebuggerFoundation.Debugger.LLDB',
                    'selectedLaunchIdentifier': 'Xcode.DebuggerFoundation.Debugger.LLDB',
                    'shouldUseLaunchSchemeArgsEnv': 'YES',
                    'buildConfiguration': 'debug'
                }
            )
            node._add(test_action, 'Testables')
            macro_expansion = node._add(test_action, 'MacroExpansion')
            launch_action = node._add(
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
            buildable_product_runnable = node._add(launch_action, 'BuildableProductRunnable')
            node._add(launch_action, 'AdditionalOptions')
            profile_action = node._add(
                scheme, 'ProfileAction', {
                    'buildConfiguration': 'profile',
                    'shouldUseLaunchSchemeArgsEnv': 'YES',
                    'savedToolIdentifier': '',
                    'useCustomWorkingDirectory': 'NO',
                    'debugDocumentVersioning': 'NO'
                }
            )
            buildable_product_runnable2 = node._add(profile_action, 'BuildableProductRunnable')
            node._add(scheme, 'AnalyzeAction', {'buildConfiguration': 'debug'})
            node._add(scheme, 'ArchiveAction', {'buildConfiguration': 'final', 'revealArchiveInOrganizer': 'YES'})
            for el in [build_action_entry, macro_expansion, buildable_product_runnable, buildable_product_runnable2]:
                node._add(
                    el, 'BuildableReference', {
                        'BuildableIdentifier': 'primary',
                        'BlueprintIdentifier': identifier,
                        'BuildableName': product,
                        'BlueprintName': name,
                        'ReferencedContainer': 'container:%s' % project
                    }
                )
        else:
            build_action_entry = node._add(
                build_action_entries, 'BuildActionEntry', {
                    'buildForTesting': 'NO',
                    'buildForRunning': 'NO',
                    'buildForProfiling': 'NO',
                    'buildForArchiving': 'NO',
                    'buildForAnalyzinf': 'NO'
                }
            )
            node._add(
                build_action_entry, 'BuildableReference', {
                    'BuildableIdentifier': 'primary',
                    'BlueprintIdentifier': identifier,
                    'BuildableName': product,
                    'BlueprintName': name,
                    'ReferencedContainer': 'container:%s' % project
                }
            )
        node.write(self.outputs[0])
        return None


@build_framework.autosig_generator('schemes')
class xcode_schememgmt(waflib.Task.Task):
    def run(self) -> Optional[int]:
        node = XmlNode()
        plist = node._add(node.document, 'plist', {'version': '1.0'})
        dict_value = node._add(plist, 'dict')
        node._add(dict_value, 'key', 'SchemeUserState')
        userstates = node._add(dict_value, 'dict')

        node._add(dict_value, 'key', 'SuppressBuildableAutocreation')
        autocreation = node._add(dict_value, 'dict')

        index = 0
        schemes = getattr(self.generator, 'schemes')  # type: List[Tuple[str, bool]]
        for scheme, dummy in schemes:
            node._add(userstates, 'key', scheme)
            dict_value = node._add(userstates, 'dict')
            node._add(dict_value, 'key', 'isShown')
            if dummy:
                node._add(dict_value, 'false')
            else:
                node._add(dict_value, 'true')
            node._add(dict_value, 'key', 'orderHint')
            node._add(dict_value, 'integer', str(index))
            node._add(autocreation, 'key', scheme)
            dict_value = node._add(autocreation, 'dict')
            node._add(dict_value, 'key', 'primary')
            node._add(dict_value, 'true')
            index += 1
        node.write(self.outputs[0])
        return None


_ProjectList = List[Tuple[str, str, List[waflib.Node.Node], List[str], List[Tuple[str, waflib.Node.Node]]]]


@build_framework.autosig_generator('targets')
@build_framework.autosig_env('ALL_TOOLCHAINS', 'ALL_VARIANTS')
class xcode_project(waflib.Task.Task):

    def run(self) -> Optional[int]:
        build_context = self.generator.bld
        assert isinstance(build_context, build_framework.ProjectGenerator)
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME,
                          os.path.basename(build_context.srcnode.abspath()))

        p = PBXProject(appname, ('Xcode 3.2', 46), build_context)

        targets = getattr(self.generator, 'targets')  # type: _ProjectList
        for identifier, target, include_nodes, defines, source_nodes in targets:
            p.add(
                identifier,
                target,
                include_nodes,
                defines,
                source_nodes,
                build_context.srcnode,
                build_context.env.ALL_VARIANTS
            )

        for toolchain in build_context.env.ALL_TOOLCHAINS:
            env = build_context.all_envs[toolchain]
            if env.SUB_TOOLCHAINS:
                bld_env = build_context.all_envs[env.SUB_TOOLCHAINS[0]]
                all_envs = [build_context.all_envs[t] for t in env.SUB_TOOLCHAINS]
            else:
                bld_env = env
                all_envs = [env]
            identifier = bld_env._XCODE_TARGET_ID
            if bld_env.XCODE_ABI == 'mach_o':
                variants = []
                plist_filename = ''
                for task_gen, plist_node in self.generator.env.PLIST_FILES:
                    if build_framework.apply_source_filter(task_gen, bld_env, plist_node)[0]:
                        plist_filename = plist_node.path_from(build_context.srcnode)
                        print(plist_filename)
                for variant in self.env.ALL_VARIANTS:
                    variants.append(
                        XCBuildConfiguration(
                            variant, {
                                'PRODUCT_NAME':
                                    appname,
                                'PRODUCT_BUNDLE_IDENTIFIER':
                                    'Motor.motor',
                                'BUILT_PRODUCTS_DIR':
                                    os.path.join(build_context.srcnode.abspath(), env.PREFIX, variant),
                                'CONFIGURATION_BUILD_DIR':
                                    os.path.join(build_context.srcnode.abspath(), env.PREFIX, variant),
                                'ARCHS':
                                    ' '.join([_macarch(e.VALID_ARCHITECTURES[0]) for e in all_envs]),
                                'VALID_ARCHS':
                                    ' '.join([_macarch(e.VALID_ARCHITECTURES[0]) for e in all_envs]),
                                'SDKROOT':
                                    bld_env.XCODE_SDKROOT,
                                '%s_DEPLOYMENT_TARGET' % bld_env.XCODE_SUPPORTEDPLATFORMS.upper():
                                    bld_env.MACOSX_SDK_MIN,
                                'SUPPORTED_PLATFORMS':
                                    bld_env.XCODE_SUPPORTEDPLATFORMS,
                                'INFOPLIST_FILE':
                                    plist_filename
                            }
                        )
                    )
                build = PBXShellScriptBuildPhase('build:' + toolchain + ':${CONFIG} --werror')
                native_target = PBXNativeTarget(
                    identifier, toolchain,
                    PBXFileReference(appname, appname + '.app', 'wrapper.application', 'BUILT_PRODUCTS_DIR'),
                    "com.apple.product-type.application", [build], variants
                )
                p.targets.append(native_target)
                getattr(p, '_output').children.append(native_target.productReference)
            else:
                legacy_target = PBXLegacyTarget(identifier, 'build:%s:$(CONFIG) --werror' % toolchain, toolchain,
                                                build_context.bldnode)
                p.targets.append(legacy_target)
        p.write(open(self.outputs[0].abspath(), 'w'))
        return None


@waflib.TaskGen.feature('motor:cxx')
@waflib.TaskGen.after_method('apply_incpaths')
def make_xcode_scheme(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'xcode' in task_gen.env.PROJECTS:
        import getpass
        xcode_project = getattr(task_gen.bld, 'xcode_project')  # type: waflib.TaskGen.task_gen
        scheme_node = build_framework.make_bld_node(
            xcode_project,
            None,
            'xcuserdata/%s.xcuserdatad/xcschemes' % getpass.getuser(),
            'index.%s.xcscheme' % task_gen.target
        )
        scheme_node.parent.mkdir()

        identifier = _new_xcode_id()
        xcode_project.create_task(
            'xcode_scheme',
            [],
            [scheme_node],
            identifier=identifier,
            scheme_name='index.' + task_gen.target,
            product='lib%s.a' % task_gen.target,
            project=xcode_project.name,
            dummy=True
        )
        build_framework.install_files(
            xcode_project,
            '%s/%s/xcuserdata/%s.xcuserdatad/xcschemes' % (
                xcode_project.bld.srcnode.abspath(), xcode_project.target, getpass.getuser()),
            [scheme_node]
        )
        getattr(xcode_project, 'schemes').append((scheme_node.name, True))
        getattr(xcode_project, 'targets').append((
            identifier,
            task_gen.target,
            getattr(task_gen, 'includes_nodes'),
            getattr(task_gen, 'defines'),
            getattr(task_gen, 'source_nodes'),
        ))


@waflib.TaskGen.feature('motor:xcode')
def make_xcodeproj(task_gen: waflib.TaskGen.task_gen) -> None:
    import getpass
    appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, os.path.basename(task_gen.bld.srcnode.abspath()))
    project = build_framework.make_bld_node(task_gen, None, None, 'project.pbxproj')
    project.parent.mkdir()
    task_gen.create_task('xcode_project', [], [project])
    build_framework.install_files(
        task_gen,
        os.path.join(task_gen.bld.srcnode.abspath(), task_gen.target),
        [project]
    )

    schemes = getattr(task_gen, 'schemes')  # type: List[Tuple[str, bool]]
    scheme_nodes = []

    for toolchain in task_gen.env.ALL_TOOLCHAINS:
        env = task_gen.bld.all_envs[toolchain]
        if env.SUB_TOOLCHAINS:
            bld_env = task_gen.bld.all_envs[env.SUB_TOOLCHAINS[0]]
            all_envs = [task_gen.bld.all_envs[t] for t in env.SUB_TOOLCHAINS]
        else:
            bld_env = env
            all_envs = [env]
        identifier = _new_xcode_id()
        scheme_node = build_framework.make_bld_node(
            task_gen,
            None,
            'xcuserdata/%s.xcuserdatad/xcschemes' % getpass.getuser(),
            '%s.xcscheme' % toolchain
        )
        bld_env._XCODE_TARGET_ID = identifier
        if bld_env.XCODE_ABI == 'mach_o':
            product = appname + '.app'
        else:
            product = appname

        task_gen.create_task(
            'xcode_scheme',
            [],
            [scheme_node],
            identifier=identifier,
            scheme_name=toolchain,
            product=product,
            project=task_gen.name,
            dummy=False
        )
        scheme_nodes.append(scheme_node)
        schemes.append((scheme_node.name, False))

    schememgmt_node = build_framework.make_bld_node(
        task_gen,
        None,
        'xcuserdata/%s.xcuserdatad/xcschemes' % getpass.getuser(),
        'xcschememanagement.plist'
    )
    task_gen.create_task('xcode_schememgmt', [], [schememgmt_node], schemes=schemes)
    build_framework.install_files(
        task_gen,
        '%s/%s/xcuserdata/%s.xcuserdatad/xcschemes' % (
            task_gen.bld.srcnode.abspath(), task_gen.target, getpass.getuser()),
        scheme_nodes + [schememgmt_node]
    )


def build(build_context: build_framework.BuildContext) -> None:
    if 'xcode' in build_context.env.PROJECTS:
        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME,
                          os.path.basename(build_context.srcnode.abspath()))
        schemes = []  # type: List[Tuple[str, bool]]
        xcode_project = build_context(
            appname + '.xcodeproj',
            target=appname + '.xcodeproj',
            features='motor:xcode',
            group=build_context.cmd,
            schemes=schemes,
            targets=[],
        )
        setattr(build_context, 'xcode_project', xcode_project)
