import os
import elftools.elf.elffile
import elftools.common.exceptions
import waflib.Options
from ..options import ConfigurationContext
from .target.compiler import get_sysroot_libpaths
from typing import Optional

PLATFORMS = {
    'ELFOSABI_SYSV': 'linux',
    'ELFOSABI_LINUX': 'linux',
    'ELFOSABI_FREEBSD': 'pc-freebsd',
    'ELFOSABI_SOLARIS': 'solaris',
}
ARCHITECTURES = {
    'EM_386': 'i386',
    'EM_X86_64': 'x86_64',
    'EM_PPC': 'ppc',
    'EM_PPC64': 'ppc64',
    'EM_ARM': 'arm',
    'EM_AARCH64': 'aarch64',
}

LITTLE_ENDIAN = {
    'arm': 'armel',
    'aarch64': 'aarch64',
    'ppc64': 'ppc64le',
}

BIG_ENDIAN = {
    'arm': 'armbe',
}

ARM_NAMES = {
    0: 'Pre-v4',
    1: 'v4',
    2: 'v4T',
    3: 'v5T',
    4: 'v5TE',
    5: 'v5TEJ',
    6: 'v6',
    7: 'v6KZ',
    8: 'v6T2',
    9: 'v6K',
    10: 'v7',
    11: 'v6-M',
    12: 'v6S-M',
    13: 'v7E-M',
    14: 'v8',
    15: 'v8-R',
    16: 'v8-M.baseline',
    17: 'v8-M.mainline',
}

MULTILIB_DIRS = {
    'arm': {
        'v5': 'armv5',
        'v6': 'armv6',
        'v7': 'armv7',
    },
    'x86':
        {
            '64': 'x86_64',
            'amd64': 'x86_64',
            'x86_64': 'x86_64',
            'i386': 'i386',
            'i486': 'i486',
            'i586': 'i586',
            'i686': 'i686',
        },
    'i386': {
        '64': 'x86_64',
        'amd64': 'x86_64',
        'x86_64': 'x86_64',
        'i486': 'i486',
        'i586': 'i586',
        'i686': 'i686',
    },
    'i486': {
        '64': 'x86_64',
        'amd64': 'x86_64',
        'x86_64': 'x86_64',
        'i386': 'i386',
        'i586': 'i586',
        'i686': 'i686',
    },
    'i586': {
        '64': 'x86_64',
        'amd64': 'x86_64',
        'x86_64': 'x86_64',
        'i386': 'i386',
        'i486': 'i486',
        'i686': 'i686',
    },
    'i686': {
        '64': 'x86_64',
        'amd64': 'x86_64',
        'x86_64': 'x86_64',
        'i386': 'i386',
        'i486': 'i486',
        'i586': 'i586',
    },
    'x86_64': {
        '32': 'i386',
        'i386': 'i386',
        'i486': 'i486',
        'i586': 'i586',
        'i686': 'i686',
    },
    'ppc': {
        '64': 'ppc64',
        'ppc64': 'ppc64',
        'powerpc64': 'powerpc64'
    },
    'powerpc': {
        '64': 'powerpc64',
        'ppc64': 'ppc64',
        'powerpc64': 'powerpc64'
    },
    'ppc64': {
        '32': 'ppc',
        'ppc': 'ppc',
        'powerpc': 'powerpc'
    },
    'powerpc64': {
        '32': 'powerpc',
        'ppc': 'ppc',
        'powerpc': 'powerpc'
    }
}


def configure_sysroot(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.SYSROOTS = []
    for sysroot in waflib.Options.options.sysroots:
        targets = []
        configuration_context.start_msg('Checking sysroot %s' % sysroot)
        try:
            # try to find GCC triples
            gcc_targets = os.listdir(os.path.join(sysroot, 'usr', 'lib', 'gcc'))
        except OSError:
            for libpath in get_sysroot_libpaths(sysroot):
                try:
                    content = os.listdir(libpath)
                except OSError:
                    pass
                else:
                    for item in content:
                        path = os.path.join(libpath, item)
                        platform = None  # type: Optional[str]
                        arch = None  # type: Optional[str]
                        suffix = None  # type: Optional[str]
                        abi = None  # type: Optional[str]
                        if os.path.isfile(path):
                            with open(path, 'rb') as elffile:
                                try:
                                    elf = elftools.elf.elffile.ELFFile(elffile)
                                except elftools.common.exceptions.ELFError:
                                    pass
                                else:
                                    platform = PLATFORMS.get(elf.header.e_ident['EI_OSABI'], platform)
                                    arch = ARCHITECTURES.get(elf.header.e_machine, arch)
                                    if arch == 'arm':
                                        abi_flags = elf.header.e_flags >> 24
                                        if abi_flags != 0:
                                            abi = 'gnueabi'
                                        for section in elf.iter_sections():
                                            if section['sh_type'] == 'SHT_ARM_ATTRIBUTES':
                                                for subsection in section.iter_subsections():
                                                    for subsubsection in subsection.iter_subsubsections():
                                                        for attribute in subsubsection.attributes:
                                                            if attribute.tag == 'TAG_ABI_VFP_ARGS':
                                                                suffix = 'hf'
                                                            if attribute.tag == 'TAG_CPU_ARCH':
                                                                arch += ARM_NAMES[attribute.value]
                                    if elf.header.e_ident['EI_DATA'] == 'ELFDATA2LSB':
                                        if arch is not None:
                                            arch = LITTLE_ENDIAN.get(arch, arch)
                                    elif elf.header.e_ident['EI_DATA'] == 'ELFDATA2MSB':
                                        if arch is not None:
                                            arch = BIG_ENDIAN.get(arch, arch)
                                    if suffix is not None:
                                        # arch = arch + suffix
                                        if abi is not None:
                                            abi = abi + suffix
                                    elif elf.header.e_flags & 0x00000400:
                                        if arch is not None:
                                            arch = arch + 'hf'
                                    if platform is not None and arch is not None:
                                        if abi is not None:
                                            targets.append('%s-%s-%s' % (arch, platform, abi))
                                        else:
                                            targets.append('%s-%s' % (arch, platform))
                                    break
        else:
            for target in gcc_targets:
                gcc_target_path = os.path.join(sysroot, 'usr', 'lib', 'gcc', target)
                target_arch = target.split('-')[0]

                for version in os.listdir(gcc_target_path):
                    if target not in targets:
                        targets.append(target)
                    gcc_target_version_path = os.path.join(gcc_target_path, version)
                    for multilib in os.listdir(gcc_target_version_path):
                        if os.path.isfile(os.path.join(gcc_target_version_path, multilib, 'libgcc.a')):
                            try:
                                multilib_arch = MULTILIB_DIRS[target_arch][multilib]
                            except KeyError:
                                print('unknown multilib: %s/%s' % (arch, multilib))
                            else:
                                multilib_target = '-'.join([multilib_arch] + target.split('-')[1:])
                                if multilib_target not in targets:
                                    targets.append(multilib_target)

        configuration_context.env.append_value('SYSROOTS', [(sysroot, targets)])
        configuration_context.end_msg(', '.join(targets))
