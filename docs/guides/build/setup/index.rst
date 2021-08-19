Building Motor from source
##############################

Setting up a build environment
******************************

In order to build the engine from source, the following components are required:

- A host running Linux, macOS, FreeBSD, Solaris or Windows
- Python (version 2.7 or 3.4+)
- Flex and Bison
- A C++ compiler in the path or installed in a standard location
   - Clang version 2.9 or above
   - GCC version 3.4 or above
   - SunCC version 5.11 or above
   - Microsoft Visual Studio 2003 or above
   - Intel compiler, version 9 or above
- Many plugins require third party libraries in order to be enabled.

The build system will usually automatically detect compilers, Flex and Bison from the environment
and/or the registry. Some of these components can be downloaded from the GitHub release page for
certain platforms/architectures.

Since Motor is very modular, it does not strictly require any development library to be
installed, at the cost of seeing the plugin disabled. The core engine depends only on standard or
operating system libraries (threading, filesystem, etc.).

Building from the command line
******************************

.. highlight:: console

The Motor uses `WAF <https://waf.io/>`__ as the build system. The build happens in two phases:

#. The build environments will be created. 
   This step detects all available compilers (including cross compilers) and creates toolchain
   environments for each detected target. This step needs to be executed only once for the host; 

   .. container:: toggle

      .. container:: header

         ::

            ~/motor > python waf configure

      ::

         Setting top to                           : ~/motor 
         Setting out to                           : ~/motor/bld/.waf 
         Checking for program 'flex'              : /usr/bin/flex 
         Checking for program 'bison'             : /usr/bin/bison 
         Looking for clang compilers              : done 
         Looking for msvc compilers               : done 
         Looking for gcc compilers                : done 
         Looking for suncc compilers              : done 
         Looking for intel compilers              : done 
         Looking for clang 10+                    : /usr/lib/llvm-12/bin/clang++ 
         Checking for Android tools               : done 
         + configuring for platform Linux 
         `- linux_gnu_amd64-clang_amd64-11.0.1  : gnu {unit tests} 
         `- linux_gnu_amd64-clang_amd64-12.0.0  : gnu {unit tests} 
         `- linux_gnu_amd64-gcc_amd64-9.3.0     : gnu {unit tests} 
         `- linux_gnu_amd64-gcc_amd64-10.2.1    : gnu {unit tests} 
         `- linux_gnu_amd64-suncc_amd64-5.15    : sun {unit tests} 
         `- linux_gnu_x86-clang_x86-11.0.1      : gnu {unit tests} 
         `- linux_gnu_x86-clang_x86-12.0.0      : gnu {unit tests} 
         `- linux_gnu_x86-gcc_x86-9.3.0         : gnu {unit tests} 
         `- linux_gnu_x86-gcc_x86-10.2.1        : gnu {unit tests} 
         `- linux_gnu_x86-suncc_x86-5.15        : sun {unit tests} 
         + configuring for platform windows 
         `- mingw_amd64-gcc_amd64-10            : mingw 
         `- mingw_x86-gcc_x86-10                : mingw 
         + configuring for platform android 
         `- android_nougat_7.0-clang-9.0.8      : androideabi 
             `- arm64                             : androideabi 
             `- armv7a                            : androideabi 
             `- amd64                             : androideabi 
             `- x86                               : androideabi 
         Looking for CUDA                         : 11.3 
         'configure' finished successfully (19.802s)

#. The build can be started for one of the detected target environments.

   .. container:: toggle

      .. container:: header

         ::

            ~/motor > python waf build:linux_gnu_amd64-clang_amd64-12.0.0:debug

      ::

         setup not run; setting up the toolchain
         'build:linux_gnu_amd64-clang_amd64-12.0.0:debug' finished successfully (0.004s)
         Setting up environment                   : linux_gnu_amd64-clang_amd64-12.0.0 
           compute.CUDA                           : cuda 11.3 [3.5, 3.7, 5.0, 5.2, 5.3, 6.0, 6.1, 6.2, 7.0, 7.2, 7.5, 8.0] 
           compute.OpenCL                         : from pkg-config 
           compute.cpu                            : vanilla, .sse3, .sse4, .avx, .avx2 
           graphics.OpenGL                        : from pkg-config 
           graphics.OpenGLES2                     : from pkg-config 
           graphics.freetype                      : from pkg-config 
           gui.gtk3                               : from pkg-config 
           physics.bullet                         : from pkg-config 
           scripting.lua                          : version -5.4 from pkg-config 
           scripting.python                       : 2.7, 3.9 
           system.X11                             : from pkg-config 
           system.zlib                            : from pkg-config 
           system.minizip                         : from pkg-config 
         'setup:linux_gnu_amd64-clang_amd64-12.0.0' finished successfully (1.008s)
         Generating LALR tables
         Generating LALR tables
         [  1/618] {bison}       motor.reflection.pp/valueparser.cc
         [  2/618] {bison}       plugin.scripting.package.pp/packageparser.cc
         [  3/618] {master}      motor.minitl/master-cxx-0.cc
         [  4/618] {master}      motor.core/master-c-0.c
         [  5/618] {master}      motor.core/master-cxx-2.cc
         [  6/618] {master}      motor.core/master-cxx-1.cc
         [  7/618] {master}      motor.core/master-cxx-0.cc
         [  8/618] {master}      motor.network/master-cxx-0.cc
         [  9/618] {master}      motor.filesystem/master-cxx-0.cc
         [ 10/618] {master}      motor.introspect/master-cxx-0.cc
         [ 11/618] {master}      motor.settings/master-cxx-0.cc
         [ 12/618] {master}      motor.scheduler/master-cxx-0.cc
         [ 13/618] {master}      motor.plugin/master-cxx-0.cc
         [ 14/618] {master}      plugin.graphics.shadermodel1/master-cxx-1.cc
         [ 15/618] {master}      plugin.graphics.shadermodel1/master-cxx-0.cc
         [ 16/618] {master}      plugin.compute.cpu/master-cxx-0.cc
         [ 17/618] {kernel_ast}  test.compute.unittests.pp/loop.ast
         [ 18/618] {kernel_ast}  test.compute.unittests.pp/if.ast
         [ 19/618] {master}      plugin.graphics.shadermodel2/master-cxx-0.cc
         [ 20/618] {master}      plugin.scripting.pythonlib/master-cxx-1.cc
         [ 21/618] {master}      plugin.scripting.pythonlib/master-cxx-0.cc
         [ 22/618] {master}      plugin.graphics.shadermodel3/master-cxx-0.cc
         [ 23/618] {master}      plugin.compute.opencl/master-cxx-0.cc
         [ 24/618] {master}      plugin.compute.cuda/master-cxx-0.cc
         [ 25/618] {master}      plugin.graphics.windowing/master-cxx-0.cc
         [ 26/618] {master}      plugin.debug.runtime/master-cxx-0.cc
         [ 27/618] {master}      plugin.graphics.shadermodel4/master-cxx-0.cc
         [ 28/618] {clc64}       test.compute.unittests.statement.if.cl/if.64.ll
         [ 29/618] {clc32}       test.compute.unittests.statement.if.cl/if.32.ll
         [ 30/618] {clc64}       test.compute.unittests.statement.loop.cl/loop.64.ll
         [ 31/618] {clc32}       test.compute.unittests.statement.loop.cl/loop.32.ll
         [ 32/618] {nvcc}        test.compute.unittests.statement.if.cuda/if.fatbin
         [ 33/618] {nvcc}        test.compute.unittests.statement.loop.cuda/loop.fatbin
         [ 34/618] {master}      motor.launcher/master-cxx-0.cc
         [ 35/618] {master}      plugin.debug.assert/master-cxx-0.cc
         ...
         [612/618] {cxxshlib}    plugin.graphics.nullrender/libplugin.graphics.nullrender.so
         [613/618] {dbg_copy}    plugin.graphics.shadermodel4/libplugin.graphics.shadermodel4.so.debug
         [614/618] {dbg_strip}   plugin.graphics.shadermodel4/libplugin.graphics.shadermodel4.so
         [615/618] {install}     plugin.graphics.shadermodel4/libplugin.graphics.shadermodel4.so.debug
         [616/618] {dbg_copy}    plugin.graphics.nullrender/libplugin.graphics.nullrender.so.debug
         [617/618] {dbg_strip}   plugin.graphics.nullrender/libplugin.graphics.nullrender.so
         [618/618] {install}     plugin.graphics.nullrender/libplugin.graphics.nullrender.so.debug
         'build:linux_gnu_amd64-clang_amd64-12.0.0:debug' finished successfully (4.422s)
