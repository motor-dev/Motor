# set iPhone(Simulator) configuration specific options
import build_framework
import build_framework.configure.target
import build_framework.configure.target.compiler
import build_framework.configure.target.macos
from typing import List, Tuple


class iOS(build_framework.configure.target.macos.Darwin):
    NAME = 'iPhone'
    CERTIFICATE_NAME = 'iPhone Developer'
    PLATFORMS = ['ios', 'iphone', 'darwin']
    SDK_NAME = 'iphoneos'
    OS_NAME = 'iphoneos'

    @staticmethod
    def get_root_dirs(appname: str) -> Tuple[str, str]:
        return (appname + '.app',
                appname + '.app',
                appname + '.app',
                appname + '.app')

    def load_in_env(
            self,
            configuration_context: build_framework.ConfigurationContext,
            compiler: build_framework.configure.target.compiler.Compiler
    ) -> None:
        build_framework.configure.target.macos.Darwin.load_in_env(self, configuration_context, compiler)
        configuration_context.env.SYSTEM_NAME = 'apple-ios'
        if 'GCC' in compiler.NAMES:
            configuration_context.env.append_unique('LINKFLAGS_cxxshlib', ['-lgcc_eh'])
            configuration_context.env.append_unique('LINKFLAGS_cxxprogram', ['-lgcc_eh'])


class iOSSimulator(iOS):
    NAME = 'iPhoneSimulator'
    PLATFORMS = ['ios', 'iphonesimulator', 'darwin']
    SDK_NAME = 'iphonesimulator'
    OS_NAME = 'iphoneos'


class WatchOS(iOS):
    NAME = 'WatchOS'
    PLATFORMS = ['ios', 'watchos', 'darwin']
    SDK_NAME = 'watchos'
    OS_NAME = 'watchos'

    def load_in_env(
            self,
            configuration_context: build_framework.ConfigurationContext,
            compiler: build_framework.configure.target.compiler.Compiler
    ) -> None:
        iOS.load_in_env(self, configuration_context, compiler)
        configuration_context.env.SYSTEM_NAME = 'apple-watchos'


def configure(
        configuration_context: build_framework.ConfigurationContext
) -> None:
    build_framework.configure.target.Platform.platforms += [
        iOS(configuration_context),
        iOSSimulator(configuration_context),
        WatchOS(configuration_context),
    ]
