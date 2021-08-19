/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CONFIG_PLATFORM_ANDROID_HH_
#define MOTOR_CONFIG_PLATFORM_ANDROID_HH_
/**************************************************************************************************/

#define MOTOR_PLATFORM_NAME    Android
#define MOTOR_PLATFORM_ANDROID 1
#define MOTOR_PLATFORM_LINUX   1
#define MOTOR_PLATFORM_POSIX   1

#include <malloc.h>
#define malloca    alloca
#define freea(p)   (void)p
#define DIRENT_H   <dirent.h>
#define PLUGIN_EXT ".so"

/**************************************************************************************************/
#endif
