import os
import re
from typing import List, Optional, Tuple
from ...options import ConfigurationContext
from .arch import setup_arch
from .unit_tests import setup_unit_tests


class Platform:
    NAME = ''
    SUPPORTED_TARGETS = tuple()  # type: Tuple[re.Pattern[str],...]
    platforms = []  # type: List["Platform"]

    def __init__(self) -> None:
        self.directories = []  # type: List[str]

    def get_available_compilers(
            self,
            _: ConfigurationContext,
            compiler_list: List["Compiler"]
    ) -> List[Tuple["Compiler", List["Compiler"], "Platform"]]:
        result = []  # type: List[Tuple[Compiler, List[Compiler], Platform]]
        for c in compiler_list:
            for regexp in self.SUPPORTED_TARGETS:
                if regexp.match(c.platform):
                    result.append((c, [], self))
        return result

    def platform_name(self, _: "Compiler") -> str:
        return self.NAME.lower()

    def load_in_env(self, configuration_context: ConfigurationContext, compiler: "Compiler") -> None:
        raise NotImplementedError

    def add_toolchain(
            self,
            configuration_context: ConfigurationContext,
            compiler: "Compiler",
            sub_compilers: Optional[List["Compiler"]] = None,
            add: bool = True
    ) -> Optional[str]:
        toolchain = '%s_%s-%s_%s-%s' % (
            self.platform_name(compiler), compiler.arch, compiler.NAMES[0].lower(), compiler.arch_name, compiler.version
        )
        if sub_compilers:
            toolchain = '%s-%s-%s' % (self.NAME.lower(), compiler.NAMES[0].lower(), compiler.version)
        if add:
            configuration_context.start_msg('  `- %s' % toolchain)
        else:
            configuration_context.start_msg('    `- %s' % compiler.arch)
        try:
            configuration_context.setenv(toolchain, configuration_context.env)
            compiler.load_tools(configuration_context, self)
            self.load_in_env(configuration_context, compiler)
            if not sub_compilers:
                compiler.load_in_env(configuration_context, self)
            v = configuration_context.env
            v.ARCH_NAME = compiler.arch
            v.TOOLCHAIN = toolchain
            v.append_unique('DEFINES', ['MOTOR_PLATFORM=platform_%s' % v.VALID_PLATFORMS[0]])
            v.append_unique('DEFINES_static', ['MOTOR_STATIC=1'])
            if not add:
                v.ENV_PREFIX = compiler.arch + '/%s'
                v.SUBARCH = True
            else:
                v.ENV_PREFIX = '%s'
                v.SUBARCH = False
            if not sub_compilers:
                setup_arch(configuration_context)
        except Exception as e:
            configuration_context.end_msg(str(e), color='RED')
            configuration_context.variant = ''
            return None
        else:
            if not sub_compilers:
                setup_unit_tests(configuration_context)
            configuration_context.end_msg('%s%s' % (
                configuration_context.env.COMPILER_ABI,
                configuration_context.env.RUN_UNIT_TESTS and ' {unit tests}' or ''))
            # if not sub_compilers:
            #    conf.recurse(conf.motornode.abspath(), name='setup', once=False)
            if v.STATIC:
                v.append_unique('DEFINES', ['MOTOR_STATIC=1'])
            v.TMPDIR = os.path.join(configuration_context.bldnode.abspath(), toolchain)
            v.PREFIX = os.path.join('bld', toolchain)
            configuration_context.variant = ''
            for c in sub_compilers or []:
                t = self.add_toolchain(configuration_context, c, add=False)
                if t:
                    v.append_unique('SUB_TOOLCHAINS', [t])
            if add:
                configuration_context.env.append_unique('ALL_TOOLCHAINS', toolchain)
            return toolchain


from .compiler import Compiler
