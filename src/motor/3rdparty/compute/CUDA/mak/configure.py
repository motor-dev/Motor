import os
import sys
import build_framework
import waflib.Utils
from typing import Any, List, Tuple


def _find_cuda_registry_paths(all_versions_key: Any) -> List[str]:
    bindirs = []  # type: List[str]
    if sys.platform == "win32":
        import winreg
        try:
            root_path, _ = winreg.QueryValueEx(all_versions_key, 'RootInstallDir')
        except OSError:
            pass
        else:
            index = 0
            while 1:
                try:
                    version = waflib.Utils.winreg.EnumKey(all_versions_key, index)
                    version_key = waflib.Utils.winreg.OpenKey(all_versions_key, version)
                except OSError:
                    break
                index += 1
                try:
                    full_path, _ = waflib.Utils.winreg.QueryValueEx(version_key, 'InstallDir')
                except OSError:
                    full_path = os.path.join(root_path, version)
                bindirs.append(os.path.join(full_path, 'bin'))
    return bindirs


def find_cuda_paths(configuration_context: build_framework.ConfigurationContext) \
        -> List[Tuple[Tuple[int, ...], List[str]]]:
    compilers = []
    v = configuration_context.env
    environ = getattr(configuration_context, 'environ', os.environ)
    bindirs = environ['PATH'].split(os.pathsep) + v.EXTRA_PATH
    for key, value in os.environ.items():
        if key.startswith('CUDA_PATH'):
            bindirs.append(os.path.join(value, 'bin'))
    if sys.platform == 'win32':
        import winreg
        try:
            all_versions = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Wow6432node\NVIDIA Corporation\GPU Computing Toolkit\CUDA'
            )
        except OSError:
            pass
        else:
            bindirs += _find_cuda_registry_paths(all_versions)
        try:
            all_versions = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\NVIDIA Corporation\GPU Computing Toolkit\CUDA'
            )
        except OSError:
            pass
        else:
            bindirs += _find_cuda_registry_paths(all_versions)
    else:
        try:
            developer_dirs = os.listdir('/Developer/NVIDIA')
        except OSError:
            try:
                local_dirs = os.listdir('/usr/local')
            except OSError:
                pass
            else:
                for local_dir in local_dirs:
                    if local_dir.startswith('cuda'):
                        local_dir = os.path.join('/usr/local', local_dir)
                        if os.path.isdir(local_dir) and not os.path.islink(local_dir):
                            bindirs.append(os.path.join(local_dir, 'bin'))
        else:
            for cuda_dir in developer_dirs:
                cuda_dir = os.path.join('/Developer/NVIDIA', cuda_dir)
                if os.path.isdir(cuda_dir) and not os.path.islink(cuda_dir):
                    bindirs.append(os.path.join(cuda_dir, 'bin'))
    paths = [os.path.normpath(path) for path in bindirs]
    for path in paths:
        nvcc = configuration_context.find_program('nvcc', mandatory=False, path_list=[path], var='NVCC_TEMP_PROG')
        del v['NVCC_TEMP_PROG']
        if nvcc:
            try:
                p = waflib.Utils.subprocess.Popen(
                    nvcc + ['--version'],
                    stdin=waflib.Utils.subprocess.PIPE,
                    stdout=waflib.Utils.subprocess.PIPE,
                    stderr=waflib.Utils.subprocess.PIPE
                )
                out, err = p.communicate()
            except OSError:
                pass
            else:
                if p.returncode == 0:
                    if not isinstance(out, str):
                        out_str = out.decode(sys.stdout.encoding, errors='ignore')
                    else:
                        out_str = out
                    for line in out_str.split('\n'):
                        if line.startswith('Cuda compilation tools'):
                            version = line.split(',')[1].split()[1]
                            version_number = tuple(int(x) for x in version.split('.'))
                            compilers.append((version_number, nvcc))
    return compilers


def configure(configuration_context: build_framework.ConfigurationContext) -> None:
    configuration_context.start_msg('Looking for CUDA')
    v = configuration_context.env
    compilers = find_cuda_paths(configuration_context)
    if compilers:
        v.NVCC_COMPILERS = sorted(compilers)
        v.NVCC_CXXFLAGS_debug = ['-D_DEBUG', '--generate-line-info']
        v.NVCC_CXXFLAGS_profile = ['-DNDEBUG', '-O2', '--generate-line-info']
        v.NVCC_CXXFLAGS_final = ['-DNDEBUG', '-O2']
        v.NVCC_CXXFLAGS_cxx98 = ['-std=c++03']
        v.NVCC_CXXFLAGS_cxx03 = ['-std=c++03']
        v.NVCC_CXXFLAGS_cxx11 = ['-std=c++11']
        v.NVCC_CXXFLAGS_cxx14 = ['-std=c++14']
        v.NVCC_CXXFLAGS_cxx17 = ['-std=c++17']
        v.NVCC_CXXFLAGS_cxx20 = ['-std=c++17']
        v.NVCC_CXXFLAGS_cxx23 = ['-std=c++17']
        v.NVCC_CXXFLAGS = ['-c', '-x', 'cu']
        v.NVCC_CXX_SRC_F = ''
        v.NVCC_CXX_TGT_F = ['-o']
        v.NVCC_ARCH_ST = ['-arch']
        v.NVCC_FRAMEWORKPATH_ST = '-F%s'
        v.NVCC_FRAMEWORK_ST = ['-framework']
        v.NVCC_CPPPATH_ST = '-I%s'
        v.NVCC_DEFINES_ST = '-D%s'

    configuration_context.end_msg(
        ', '.join('.'.join(str(x) for x in p[0]) for p in configuration_context.env.NVCC_COMPILERS)
    )
