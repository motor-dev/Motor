/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CONFIG_PLATFORMS_PLATFORM_IOS_HH
#define MOTOR_CONFIG_PLATFORMS_PLATFORM_IOS_HH

#define MOTOR_PLATFORM_NAME  iOS
#define MOTOR_PLATFORM_IOS   1
#define MOTOR_PLATFORM_MACOS 1

#include <malloc/malloc.h>
#define malloca    alloca
#define freea(p)   (void)p
#define DIRENT_H   <dirent.h>
#define PLUGIN_EXT ".dylib"

#endif
