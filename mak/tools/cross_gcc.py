from Configure import conftest
import Options
import Utils
import re
from TaskGen import feature, before, extension, after
import os

@conftest
def get_native_gcc_target(conf):
	if not conf.env['GCC_NATIVE_TARGET']:
		cmd = ['gcc', '-v']
		try:
			p = Utils.pproc.Popen(cmd, stdin=Utils.pproc.PIPE, stdout=Utils.pproc.PIPE, stderr=Utils.pproc.PIPE)
			out = p.communicate()[1]
		except:
			return

		out = str(out).split('\n')

		for line in out:
			if line.startswith('Target:'):
				conf.env['GCC_NATIVE_TARGET'] = line.split()[1]

def parse_gcc_target(target):
	archs = [ ('i686-w64', 'amd64'),
			  ('i386', 'x86'),
			  ('i486', 'x86'),
			  ('i586', 'x86'),
			  ('i686', 'x86'),
			  ('arm-eabi', 'arm7'),
			  ('mipsel', 'mips'),
			  ('mips', 'mips'),
			  ('Gekko', 'mips'),
			  ('x86_64', 'amd64'),
			  ('x86', 'x86'),
			  ('amd64', 'amd64'),
			  ('powerpc', 'powerpc'),
			  ('psp', 'mips'),
			  ('mingw32', 'x86'),
			  ('ppu', 'powerpc'),
			  ('spu', 'powerpc')]
	for gccname,aname in archs:
		if target.find(gccname) != -1:
				return aname


@conftest
def find_cross_gcc(conf):
	target = conf.env['GCC_TARGET']
	version = conf.env['GCC_VERSION']
	versionsmall = '.'.join(version.split('.')[0:2])
	if target:
		v = conf.env
		v['GCC_CONFIGURED_ARCH'] = parse_gcc_target(target) or 'unknown'
		if not v['CC']: v['CC'] = conf.find_program(target+'-gcc-'+version, var='CC', path_list=v['GCC_PATH'])
		if not v['CC']: v['CC'] = conf.find_program(target+'-gcc-'+versionsmall, var='CC', path_list=v['GCC_PATH'])
		if not v['CC']: conf.fatal('unable to find gcc for target %s' % target)

		if not v['CXX']: v['CXX'] = conf.find_program(target+'-g++-'+version, var='CXX', path_list=v['GCC_PATH'])
		if not v['CXX']: v['CXX'] = conf.find_program(target+'-g++-'+versionsmall, var='CXX', path_list=v['GCC_PATH'])
		if not v['CXX']: v['CXX'] = conf.find_program(target+'-c++-'+version, var='CXX', path_list=v['GCC_PATH'])
		if not v['CXX']: v['CXX'] = conf.find_program(target+'-c++-'+versionsmall, var='CXX', path_list=v['GCC_PATH'])
		if not v['CXX']: v['CXX'] = conf.find_program(target+'-g++', var='CXX', path_list=v['GCC_PATH'])
		if not v['CXX']: v['CXX'] = conf.find_program(target+'-c++', var='CXX', path_list=v['GCC_PATH'])
		if not v['CXX']: conf.fatal('unable to find g++ for target %s' % target)

		if not v['CPP']: v['CPP'] = conf.find_program(target+'-cpp-'+version, var='CPP', path_list=v['GCC_PATH'])
		if not v['CPP']: v['CPP'] = conf.find_program(target+'-cpp', var='CPP', path_list=v['GCC_PATH'])
		if not v['CPP']: v['CPP'] = conf.find_program('cpp-'+version, var='CPP', path_list=v['GCC_PATH'])
		if not v['CPP']: v['CPP'] = conf.find_program('cpp-'+version[0:3], var='CPP', path_list=v['GCC_PATH'])
		if not v['CPP']: v['CPP'] = conf.find_program('cpp', var='CPP', path_list=v['GCC_PATH'])
		if not v['CPP']: conf.fatal('unable to find cpp for target %s' % target)

		if not v['AS']: v['AS'] = v['CC']

		if not v['AR']: v['AR'] = conf.find_program(target+'-gar', var='AR', path_list=v['GCC_PATH'])
		if not v['AR']: v['AR'] = conf.find_program(target+'-ar', var='AR', path_list=v['GCC_PATH'])
		if not v['AR']:
			v['AR'] = conf.find_program('gar', var='AR', path_list=v['GCC_PATH'])
		if not v['AR']:
			v['AR'] = conf.find_program('gar', var='AR')
		if not v['AR']:
			v['AR'] = conf.find_program('ar', var='AR', path_list=v['GCC_PATH'])
		if not v['AR']: conf.fatal('unable to find ar for target %s' % target)

		if not v['RANLIB']: v['RANLIB'] = conf.find_program(target+'-ranlib', var='RANLIB', path_list=v['GCC_PATH'])
		if not v['RANLIB']:
			v['RANLIB'] = conf.find_program('granlib', var='RANLIB', path_list=v['GCC_PATH'])
		if not v['RANLIB']:
			v['RANLIB'] = conf.find_program('ranlib', var='RANLIB', path_list=v['GCC_PATH'])
		if not v['RANLIB']:
			v['RANLIB'] = conf.find_program('granlib', var='RANLIB')
		if not v['RANLIB']: conf.fatal('unable to find ranlib for target %s' % target)

	conf.check_tool('gcc gxx gas')
	conf.env.append_unique('ASFLAGS', '-c')

	conf.env['CCFLAGS_warnall'] = ['-std=c99', '-Wall', '-Wextra', '-pedantic', '-Winline', '-Wno-unknown-pragmas', '-Wno-unused-parameter', '-Werror']
	conf.env['CXXFLAGS_warnall'] = ['-Wall', '-Wextra', '-Wno-unknown-pragmas', '-Wno-unused-parameter', '-Werror']

	conf.env['CCFLAGS_debug'] = ['-pipe', '-g', '-D_DEBUG']
	conf.env['CXXFLAGS_debug'] = ['-pipe', '-g', '-D_DEBUG', '-Wno-invalid-offsetof']
	conf.env['LINKFLAGS_debug'] = ['-pipe', '-g']
	conf.env['ASFLAGS_debug'] = ['-pipe', '-g', '-D_DEBUG']

	conf.env['CCFLAGS_release'] = ['-pipe', '-g', '-O1']
	conf.env['CXXFLAGS_release'] = ['-pipe', '-g', '-O1', '-Wno-invalid-offsetof']
	conf.env['ASFLAGS_release'] = ['-pipe', '-g', '-O1']
	conf.env['LINKFLAGS_release'] = ['-pipe', '-g']

	conf.env['CCFLAGS_profile'] = ['-pipe', '-g', '-DNDEBUG', '-O3']
	conf.env['CXXFLAGS_profile'] = ['-pipe', '-g', '-DNDEBUG', '-O3', '-fno-rtti', '-fno-exceptions', '-Wno-invalid-offsetof']
	conf.env['ASFLAGS_profile'] = ['-pipe', '-g', '-DNDEBUG', '-O3']
	conf.env['LINKFLAGS_profile'] = ['-pipe', '-g', '-s']

	conf.env['CCFLAGS_final'] = ['-pipe', '-g', '-DNDEBUG', '-O3']
	conf.env['CXXFLAGS_final'] = ['-pipe', '-g', '-DNDEBUG', '-O3', '-fno-rtti', '-fno-exceptions', '-Wno-invalid-offsetof']
	conf.env['ASFLAGS_final'] = ['-pipe', '-g', '-DNDEBUG', '-O3']
	conf.env['LINKFLAGS_final'] = ['-pipe', '-g', '-s']

	if v['GCC_CONFIGURED_ARCH'] in ['amd64', 'x86']:
		conf.env.append_unique('CCFLAGS', ['-mfpmath=sse', '-msse2'])
		conf.env.append_unique('CXXFLAGS', ['-mfpmath=sse', '-msse2'])

	if v['GCC_CONFIGURED_PLATFORM'] == 'wii':
		flags = ['-mcpu=750', '-mrvl', '-meabi', '-msdata=eabi', '-mhard-float', '-fmodulo-sched', '-ffunction-sections', '-fdata-sections', '-mregnames', '-Wa,-mgekko']
		conf.env.append_unique('CCFLAGS', flags)
		conf.env.append_unique('CXXFLAGS', flags)
		conf.env.append_unique('ASFLAGS', flags+['-mregnames', '-D_LANGUAGE_ASSEMBLY'])
		conf.env.append_unique('LINKFLAGS', flags)


detect = '''
get_native_gcc_target
find_cross_gcc
'''
