/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_CORE_PLATFORM_IPHONE_HH_
#define BE_CORE_PLATFORM_IPHONE_HH_
/*****************************************************************************/

#define BE_PLATFORM_NAME       iPhone
#define BE_PLATFORM_IPHONE     1
#define BE_PLATFORM_MACOS      1

#include <malloc/malloc.h>
#define malloca     alloca
#define freea(p)
#define DIRENT_H    <dirent.h>
#define PLUGIN_EXT  ".dylib"
#define PLUGIN_H    <system/plugin/posix/plugin.inl>

/*****************************************************************************/
#endif
