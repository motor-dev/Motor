/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_CORE_PLATFORMS_H_
#define BE_CORE_PLATFORMS_H_
/*****************************************************************************/

#if defined(_WIN32) && !defined(_XBOX)
# define WIN32_LEAN_AND_MEAN
# define NOMINMAX
# include <windows.h>
# pragma warning(disable:4505)
static inline void displayError()
{
    char* msg;
    ::FormatMessageA( FORMAT_MESSAGE_ALLOCATE_BUFFER|FORMAT_MESSAGE_FROM_SYSTEM,
                      0,
                      ::GetLastError(),
                      0,
                      (char*)&msg,
                      0,
                      0 );
    MessageBox(0, msg, "Win32 error", MB_OK);
    ::LocalFree(msg);
}
#define BE_WIN32_PRINTERROR()       displayError()
#define BE_WIN32_CHECKRESULT(x)     if((x) == (UINT)-1) BE_WIN32_PRINTERROR()
#endif

#ifndef _WIN32
# define OutputDebugString(s) printf("%s", s)
#endif

#if defined(_AMD64) || defined(_PPC64)
# define BE_64
#elif defined(_X86) || defined(_PPC)
# define BE_32
#elif defined(_ARM)
# define BE_32
#else
# error "unknown arch"
#endif

#if defined(_WIN32) && !defined(_XBOX)
# ifdef _AMD64
#  define BE_PLATFORM_NAME      Win64
#  define BE_PLATFORM_WIN64     1
# else
#  define BE_PLATFORM_NAME      Win32
# endif
# define BE_PLATFORM_WIN32     1
# define BE_PLATFORM_PC        1
#elif defined __APPLE__
# define BE_PLATFORM_NAME       MacOSX
# define BE_PLATFORM_MACOS      1
# define BE_PLATFORM_PC         1
#elif defined __linux__
# define BE_PLATFORM_NAME       Linux
# define BE_PLATFORM_LINUX      1
# define BE_PLATFORM_POSIX      1
# define BE_PLATFORM_PC         1
# include   <strings.h>
# define    stricmp strcasecmp
# define    strnicmp strncasecmp
#elif defined __sun
# define BE_PLATFORM_NAME       SunOS
# define BE_PLATFORM_SUN        1
# define BE_PLATFORM_POSIX      1
# define BE_PLATFORM_PC         1
#elif defined(__FreeBSD__) || defined(__OpenBSD__) || defined(__NetBSD__)
# define BE_PLATFORM_NAME       BSD
# define BE_PLATFORM_BSD        1
# define BE_PLATFORM_POSIX      1
# define BE_PLATFORM_PC         1
#elif defined _WII
# define BE_PLATFORM_NAME       Wii
# define BE_PLATFORM_WII        1
# define BE_PLATFORM_CONSOLE    1
#elif defined _XBOX360
# define BE_PLATFORM_NAME       XBox360
# define BE_PLATFORM_XBOX360    1
# define BE_PLATFORM_CONSOLE    1
#elif defined _PS3
# define BE_PLATFORM_NAME       Playstation3
# define BE_PLATFORM_PS3        1
# define BE_PLATFORM_CONSOLE    1
#else
# ifndef _PLATFORM
#  error "Unknown platform"
# else
#  define PLATFORM_INCLUDE "core/platforms/"##_PLATFORM##".hh"
#  include PLATFORM_INCLUDE
#  undef PLATFORM_INCLUDE
# endif
#endif

/*****************************************************************************/
#endif
