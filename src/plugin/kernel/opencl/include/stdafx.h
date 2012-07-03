/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_JOBS_CPU_STDAFX_H_
#define BE_JOBS_CPU_STDAFX_H_
/*****************************************************************************/

#include    <core/stdafx.h>
#include    <rtti/stdafx.h>
#include    <system/stdafx.h>

#ifdef BE_PLATFORM_MACOS
# include   <OpenCL/opencl.h>
# include   <OpenGL/OpenGL.h>
#else
# include   <opencl.h>
#endif

/*****************************************************************************/
#endif